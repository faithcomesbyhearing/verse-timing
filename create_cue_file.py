import argparse,re

parser = argparse.ArgumentParser(
        description='This function creates cue.csv file from clt file')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input audio file')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output file name')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-add_info', action='store_true', help='Add additional info: filesetid,bookname,chapter number')

args = parser.parse_args()
input_cue_file=args.i[0]
output_cue_file=args.o[0]
add_info=args.add_info


read_file=open(input_cue_file,'r')
write_file=open(output_cue_file,'w')

if add_info:
    filename = input_cue_file.split('/')[-1]
    input = re.compile('\_+').split(filename.split('.')[0])
    file_setid = input[1] + input[0]
    book_name = input[-3]
    chapter_num = input[-2]
    write_file.write(file_setid + '\n' + book_name + '\n' + chapter_num + '\n')

# Adjust decoding patterm in .clt
lines=read_file.readlines()
bits_per_second=float((lines[2]).strip())

start_time_id=3
line_number_id=5
increment=5
'''IMPL the cues in core script are recorded in the clt as cue 01 for mat 24
In core script it says +2 secs, its duration in clt is 1.66 secs'''

while line_number_id<=len(lines):

    start_time=float(lines[start_time_id].strip())/bits_per_second
    line_audio_file = (lines[line_number_id]).strip()
    line_number=(re.compile('\_+').split(line_audio_file.split('.')[0]))[-1]
    write_file.write(str(start_time)+','+str(line_number)+'\n')
    start_time_id+=increment
    line_number_id+=increment


