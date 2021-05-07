import pandas as pd,argparse,glob,statistics as stat,matplotlib.pyplot as plt,numpy as np,operator
parser = argparse.ArgumentParser(
        description='This function converts adobe audition format to audacity format')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input dir that contains the adobe audition files')
required_args.add_argument(
    '-find_string', required=True, nargs=1, type=str, help='Wild card to find name of file extension ex: curated_markers or line_markers')


args = parser.parse_args()
input_dir=args.i[0]
find_string=args.find_string[0]

conv_string_to_secs = [60, 1]



for each_file in glob.glob(input_dir+'/*'):

    file_name=(each_file.split('/')[-1]).split(find_string)[0]+'_audacity.txt'


    audacity_file=open(input_dir+'/'+file_name,'w')

    rows=open(each_file).readlines()
    for i,each_row in enumerate(rows):
        if 0 < i < len(rows):
            marker = (each_row.split('\t')[0])
            timestr = (each_row.split('\t')[1])
            current_verse_start_time = sum([a * b for a, b in zip(conv_string_to_secs, map(float, timestr.split(':')))])

            timestr = (each_row.split('\t')[2])
            current_verse_duration = sum([a * b for a, b in zip(conv_string_to_secs, map(float, timestr.split(':')))])

            current_verse_end_time=current_verse_start_time+current_verse_duration
            audacity_file.write(str(current_verse_start_time)+'\t'+str(current_verse_end_time)+'\t'+str(marker)+'\n')

    audacity_file.close()



