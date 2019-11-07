import argparse

parser = argparse.ArgumentParser(
        description='This function gets the silence boundaries given an input audio file')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input audio file')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output file name')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-db', default=[5], nargs=1, type=int, help='Threshold decibel level')
optional_args.add_argument('-sl', default=[300], nargs=1, type=int, help='Min. silence length(secs)')

args = parser.parse_args()
input_audio_file=args.i[0]
output_silence_file=args.o[0]
decibels=args.db[0]
min_sil_len=args.sl[0]


import pydub.silence as sil,os,re
from pydub import AudioSegment

filename=input_audio_file.split('/')[-1]
input=re.compile('\_+').split(filename.split('.')[0])
file_setid=input[-1]
book_name=input[-2]
chapter_num=input[-3]

sound = AudioSegment.from_mp3(input_audio_file)
dBFS = sound.dBFS
silence_boundaries = sil.detect_silence(sound, min_silence_len=min_sil_len, silence_thresh=dBFS - decibels)
if os.path.exists(output_silence_file): os.remove(output_silence_file)
silence_file=open(output_silence_file,'w')

#Add 4 lines
silence_file.write('# -'+str(decibels)+'\n')
silence_file.write(file_setid + '\n')
silence_file.write(book_name + '\n')
silence_file.write(chapter_num + '\n')

line_inc=0
for boundaries in silence_boundaries:
    line_inc+=1
    boundaries=[x/1000 for x in boundaries]
    silence_file.write("{0},{1},{2}\n".format(line_inc,boundaries[0],boundaries[1]))
    # print("{0} {1} silence".format(boundaries[0],boundaries[1]))
silence_file.close()