import argparse,re

parser = argparse.ArgumentParser(
        description='This function creates cue.csv file from clt file')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input audio file')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output file name')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-fileset', nargs=1, type=str,help='custom fileset id')
optional_args.add_argument('-book', nargs=1, type=str, help='custom book id')
optional_args.add_argument('-chapter', nargs=1, type=str,help='custom chapter id')
optional_args.add_argument('-noheader', action='store_true', help='Remove header: fileset,book,chapter,db,sId,sBegin,sEnd')

args = parser.parse_args()
input_file=args.i[0]
output_file=args.o[0]


# Open read and write files
read_file=open(input_file,'r')
write_file=open(output_file,'w')


# Write header
if not(args.noheader):write_file.write('fileset,book,chapter,line,qtime\n')

#Fill the header values and overwrite custom option
filename=input_file.split('/')[-1]
input=re.compile('\_+').split(filename.split('.')[0])
if args.fileset is not None:file_setid=args.fileset[0]
else:file_setid=input[1]+input[0]
if args.book is not None: book_name=args.book[0]
else:book_name=input[-3]
if args.chapter is not None:chapter_num=args.chapter[0]
else:chapter_num=input[-2]

# Adjust decoding patterm in .clt
lines=read_file.readlines()
bits_per_second=float((lines[2]).strip())

start_time_id=3
line_number_id=5
increment=5
'''IMPL the cues in core script are recorded in the clt as cue 01 for mat 24
In core script it says +2 secs, its duration in clt is 1.66 secs'''

while line_number_id<=len(lines):

    start_time=round(float(lines[start_time_id].strip())/bits_per_second,3)
    line_audio_file = (lines[line_number_id]).strip()
    line_number=(re.compile('\_+').split(line_audio_file.split('.')[0]))[-1]
    write_file.write(file_setid + ',' + book_name + ',' + chapter_num +',')
    write_file.write(str(line_number)+','+str(start_time)+'\n')
    start_time_id+=increment
    line_number_id+=increment

