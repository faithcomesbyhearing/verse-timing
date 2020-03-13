import os,re,csv,argparse
import pydub.silence as sil
from pydub import AudioSegment

parser = argparse.ArgumentParser(
        description='This function gets the silence boundaries given an input audio file in the foll. format fileset,book,chapter,db,sId,sBegin,sEnd')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input audio file')

# below 8,300 observed to well-correspond to line boundaries in B01___01_Matthew_____ENGESVN1DA.mp3
optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-db', default=[8], nargs=1, type=int, help='Threshold decibel level')
optional_args.add_argument('-sl', default=[300], nargs=1, type=int, help='Min. silence length(milli secs)')
optional_args.add_argument('-fileset', nargs=1, type=str,help='custom fileset id')
optional_args.add_argument('-book', nargs=1, type=str, help='custom book id')
optional_args.add_argument('-chapter', nargs=1, type=str,help='custom chapter id')
optional_args.add_argument('-noheader', action='store_true', help='Remove header: fileset,book,chapter,db,sId,sBegin,sEnd')
optional_args.add_argument('-lab', nargs=1, type=str, help='output labels file')
optional_args.add_argument('-o', nargs=1, type=str, help='output csv file')

args = parser.parse_args()
input_file=args.i[0]
decibels=args.db[0]
min_sil_len=args.sl[0]

#Fill the header values and overwrite custom option
filename=input_file.split('/')[-1]
input=re.compile('\_+').split(filename.split('.')[0])

if args.fileset is not None:file_setid=args.fileset[0]
else:file_setid=input[-1]
if args.book is not None: book_name=args.book[0]
else:book_name=input[-2]
if args.chapter is not None:chapter_num=args.chapter[0]
else:chapter_num=input[-3]
if args.lab is None: args.lab=os.path.splitext(args.i[0])[0]+'.lab'
if args.o   is None: args.o  =os.path.splitext(args.i[0])[0]+'.csv'

#Open the write file
if os.path.exists(args.o): os.remove(args.o)
write_file=open(args.o,'w')

# Write header
if not(args.noheader):write_file.write('fileset,book,chapter,db,sId,sBegin,sEnd\n')

sound = AudioSegment.from_mp3(input_file)
dBFS = sound.dBFS
silence_boundaries = sil.detect_silence(sound, min_silence_len=min_sil_len, silence_thresh=dBFS - decibels)

outfile = open(args.lab, 'w', newline='')
tsv = csv.writer(outfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
# a file ready for import as labels by audacity

line_inc=0
for boundaries in silence_boundaries:
    line_inc+=1
    boundaries=[x/1000 for x in boundaries] # convert from millisec to sec
    write_file.write(file_setid + ',' + book_name + ',' + chapter_num + ',' + '-' + str(decibels)+',')
    write_file.write("{0},{1},{2}\n".format(line_inc,boundaries[0],boundaries[1]))
    tsv.writerow([boundaries[0],boundaries[1],str(line_inc)+": "+str(round(boundaries[1]-boundaries[0],2))])
    # print("{0} {1} silence".format(boundaries[0],boundaries[1]))
write_file.close()
outfile.close()