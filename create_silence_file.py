import argparse,pydub.silence as sil,os,re
from pydub import AudioSegment

parser = argparse.ArgumentParser(
        description='This function gets the silence boundaries given an input audio file in the foll. format fileset,book,chapter,db,sId,sBegin,sEnd')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input audio file')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output file name')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-db', default=[5], nargs=1, type=int, help='Threshold decibel level')
optional_args.add_argument('-sl', default=[500], nargs=1, type=int, help='Min. silence length(milli secs)')
optional_args.add_argument('-fileset', nargs=1, type=str,help='custom fileset id')
optional_args.add_argument('-book', nargs=1, type=str, help='custom book id')
optional_args.add_argument('-chapter', nargs=1, type=str,help='custom chapter id')
optional_args.add_argument('-noheader', action='store_true', help='Remove header: fileset,book,chapter,db,sId,sBegin,sEnd')


args = parser.parse_args()
input_file=args.i[0]
output_file=args.o[0]
decibels=args.db[0]
min_sil_len=args.sl[0]

#Open the write file
if os.path.exists(output_file): os.remove(output_file)
write_file=open(output_file,'w')

# Write header
if not(args.noheader):write_file.write('fileset,book,chapter,db,sId,sBegin,sEnd\n')

#Fill the header values and overwrite custom option
filename=input_file.split('/')[-1]
input=re.compile('\_+').split(filename.split('.')[0])
if args.fileset is not None:file_setid=args.fileset[0]
else:file_setid=input[-1]
if args.book is not None: book_name=args.book[0]
else:book_name=input[-2]
if args.chapter is not None:chapter_num=args.chapter[0]
else:chapter_num=input[-3]


sound = AudioSegment.from_mp3(input_file)
dBFS = sound.dBFS
silence_boundaries = sil.detect_silence(sound, min_silence_len=min_sil_len, silence_thresh=dBFS - decibels)


line_inc=0
for boundaries in silence_boundaries:
    line_inc+=1
    boundaries=[x/1000 for x in boundaries]
    write_file.write(file_setid + ',' + book_name + ',' + chapter_num + ',' + '-' + str(decibels)+',')
    write_file.write("{0},{1},{2}\n".format(line_inc,boundaries[0],boundaries[1]))
    # print("{0} {1} silence".format(boundaries[0],boundaries[1]))
write_file.close()