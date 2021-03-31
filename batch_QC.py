import pandas as pd,argparse,glob,statistics as stat,matplotlib.pyplot as plt,numpy as np,operator,sys,os,re,matplotlib,csv
import math
import matplotlib.pyplot as plt
from matplotlib import gridspec
from collections import OrderedDict
from scipy.stats import mstats
import pathlib


#Make sure for chinanteco line comparison the cue info first liine is taken care of

parser = argparse.ArgumentParser(
        description='This function gives quality control metric between cue info and aeneas. Assumes that each line in core script is translated'
                    'to cue info and aeneas, otherwise script fails')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-cue_info_dir', required=True, nargs=1, type=str, help='Input dir that contains *cue_info*.txt')
required_args.add_argument(
    '-sab_timing_dir', required=True, nargs=1, type=str, help='Input dir that contains SAB timing files *timing.txt')
required_args.add_argument(
    '-aeneas_dir', required=True, nargs=1, type=str, help='Input dir that contains aeneas.csv')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output dir to store histograms')
required_args.add_argument(
    '-input_book_to_audiobookid_mapfile', required=True, nargs=1, type=str, help='Input file which contains mapping for book to audio book id')


optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-strict_comparison', type=int,choices=[1,2], help='1-Compare aeneas and qinfo start boundaries. 2- Compare verse duration and 1')
optional_args.add_argument('-extract_verse_timing', action='store_true', help='Compare verse timing info.')
optional_args.add_argument('-synced_silence', action='store_true', help='Indicate whether the output from aeneas timing was fully synced with silence adjustment')
optional_args.add_argument('-synced_qinfo', action='store_true', help='Indicate whether the output from aeneas timing was fully synced with qinfo')
optional_args.add_argument('-print_chapter', nargs=1, type=str,default=['9'],help='Print chapter')
optional_args.add_argument('-write_audition_format', action='store_true', help='Write output to audition tab csv format')
optional_args.add_argument('-check_secs', nargs=1, type=str,default=['3'],help='Mark if above check secs')

args = parser.parse_args()
cue_dir=args.cue_info_dir[0]
sab_dir=args.sab_timing_dir[0]
aeneas_dir=args.aeneas_dir[0]
output_dir=args.o[0]
book_to_audio_map=args.input_book_to_audiobookid_mapfile[0]

if args.strict_comparison is not None: strict_comparison=args.strict_comparison
else:strict_comparison=0
print_chapter=args.print_chapter[0]

if args.extract_verse_timing: target='verse_number'
else:target='line_number'

if args.synced_silence: aeneas_adjusted_file='*_sync_adjusted.txt'
elif args.synced_qinfo:aeneas_adjusted_file='*_qinfo_adjusted.txt'
else:aeneas_adjusted_file='*_adjusted.txt'

print(args)


if not os.path.isdir(output_dir):
    os.mkdir(output_dir)


input_file='aeneas.csv'
df=(pd.read_csv(aeneas_dir+'/'+input_file, encoding='utf-8')).astype(str)

#Get unique book and chapters
book_list=df['book'].unique()

cue_id=0
qc_data = dict()
median_dict = dict()
std_dev_dict = dict()


def do_plot(ax):
    ax.plot([1, 2, 3], [4, 5, 6], 'k.')


qc_filename=   os.path.join(output_dir,'_'.join((aeneas_dir.replace('/','_')).split('_')[-2:])+'_QC_data.csv')
with open(qc_filename, 'w') as file:
    file.write('line_number,book,chapter,verses,cueinfo_duration,aeneas_duration,abs(cuedur-aeneasdur)\n')
file.close()

for each_book in book_list:
    print(each_book)

    chapter_list=df[df['book']==each_book]['chapter'].unique()

    #print(chapter_list)
    qc_data[each_book] = dict()
    median_dict[each_book] = dict()
    std_dev_dict[each_book] = dict()
    for each_chapter in chapter_list:


        cue_id+=1


        sab_df = pd.read_csv(book_to_audio_map)
        book_id = (sab_df[(sab_df.iloc[:, 0].str).contains(each_book) == True].iloc[0, 2])
        id = (sab_df[(sab_df.iloc[:, 0].str).contains(each_book) == True].iloc[0, 1])

        id=str(id).zfill(2)


        each_chapter=str(each_chapter).zfill(2)
        SAB_timing_filename = glob.glob(sab_dir + '/*' + '-'.join(['C01', id, book_id, each_chapter, '*timing.txt']))[0]
        #print(SAB_timing_filename)



        #Make it a 3 digit acc. to cue info file naming
        find_cue_id=str(cue_id).zfill(3)
        cue_book_id = (sab_df[(sab_df.iloc[:, 0].str).contains(each_book) == True].iloc[0, 0])
        # print(cue_book_id)
        cue_info_file=glob.glob(   cue_dir+'/*'+'_'.join([find_cue_id, cue_book_id, each_chapter])+'*cue_info.txt'       )[0]
        #print(cue_info_file)

        sab_read_file=open(SAB_timing_filename).readlines()
        cue_read_file=open(cue_info_file).readlines()

        # print(len(sab_read_file),len(cue_read_file))

        if len(sab_read_file)!=len(cue_read_file):
            print(len(sab_read_file), len(cue_read_file))
            print(sab_read_file,cue_info_file)
            colnames = ['start', 'end', 'line_num']
            cue_df = pd.read_csv(cue_info_file, names=colnames, sep='\t', dtype={'start':'float64','end':'float64','line_num':'str'},header=None)


            cue_df=cue_df[cue_df.line_num.str.lstrip('0')[0].isdigit() and cue_df.line_num.str.isnumeric()]

            cue_df = cue_df.drop_duplicates(subset=['line_num'], keep='first')
            cue_df['start'] = round((cue_df['start']), 3)
            cue_df['end'] = round((cue_df['end']), 3)
            cue_df.to_csv(cue_info_file, sep='\t', index=None, header=None)

        cue_read_file = open(cue_info_file).readlines()

        colnames = ['start', 'end', 'line_num']
        sab_read_df=pd.read_csv(SAB_timing_filename, names=colnames, sep='\t', dtype={'start':'float64','end':'float64','line_num':'str'},header=None)



        for i,line in enumerate(cue_read_file):

            line = str(cue_read_file[i]).split('\t')[2]

            if any(c.isalpha() for c in (str(line.split('\n')[0]))):
                line_num = (str(line.split('\n')[0]))
            else:
                line_num=(str(line.split('\n')[0])).lstrip('0')



            verses=df[df['line_number']==line_num]['verse_number'].to_string(index=False)
            verse_trim=(str(verses).strip()).replace('\n','|').replace(' ','').lstrip('0')
            if len(verse_trim.split('|'))>1 and verse_trim.split('|')[1]=='0':verse_trim=verse_trim.split('|')[0]

            sab_line_df=sab_read_df[sab_read_df['line_num']==line_num]
            if len(sab_line_df)>0:


                sab_start=float(str(sab_line_df['start'].to_string(index=False)))
                sab_end=float(str(sab_line_df['end'].to_string(index=False)))
                sab_duration=round(sab_end-sab_start,2)
                sab_line=(str(sab_line_df['line_num'].to_string(index=False))).lstrip('0')

                cue_start=float(str(cue_read_file[i]).split('\t')[0])
                cue_end=float(str(cue_read_file[i]).split('\t')[1])
                cue_duration=round(cue_end-cue_start,2)



                difference = (round(abs(cue_duration - sab_duration), 2))

                with open(qc_filename, 'a') as file:
                    file.write("%s,%s,%s,%s,%s,%s,%s\n" % (line_num, each_book, each_chapter, verse_trim,cue_duration, sab_duration,difference))
                file.close()


qc_df=(pd.read_csv(qc_filename, encoding='utf-8'))
sorted_values=(qc_df.sort_values(by=['abs(cuedur-aeneasdur)']))['abs(cuedur-aeneasdur)']
quantiles = mstats.mquantiles(sorted_values, axis=0)

qcout_filename=   os.path.join(output_dir,'_'.join((aeneas_dir.replace('/','_')).split('_')[-2:])+'_95%QC_value.txt')

with open(qcout_filename, 'w') as file:
    file.write(str(np.quantile(sorted_values, 0.95, axis=0)))
file.close()

