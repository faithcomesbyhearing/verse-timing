import pandas as pd,argparse,glob,statistics as stat,matplotlib.pyplot as plt,numpy as np,operator,re,sys,os

parser = argparse.ArgumentParser(
        description='This function gives quality control metric between cue info and aeneas. Assumes only one book in aeneas.csv, assumes that each line in core script is translated'
                    'to cue info and aeneas, otherwise script fails')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input dir to find *sync_adjusted.txt aeneas output files')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output dir')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-fileset_id_fix_string', nargs=1, type=str,default=['KO1SKVN2DA'],help='Mark if above check secs')
optional_args.add_argument('-strict_comparison', type=int,choices=[1,2], help='1-Compare aeneas and qinfo start boundaries. 2- Compare verse duration and 1')
optional_args.add_argument('-extract_verse_timing', action='store_true', help='Compare verse timing info.')
optional_args.add_argument('-synced_silence', action='store_true', help='Indicate whether the output from aeneas timing was fully synced with silence adjustment')
optional_args.add_argument('-synced_qinfo', action='store_true', help='Indicate whether the output from aeneas timing was fully synced with qinfo')
optional_args.add_argument('-print_chapter', nargs=1, type=str,default=['9'],help='Print chapter')
optional_args.add_argument('-write_audition_format', action='store_true', help='Write output to audition tab csv format')
optional_args.add_argument('-check_secs', nargs=1, type=str,default=['3'],help='Mark if above check secs')

args = parser.parse_args()
input_dir=args.i[0]
output_dir=args.o[0]

fileset_id_fix_string=args.fileset_id_fix_string[0]


if args.strict_comparison is not None: strict_comparison=args.strict_comparison
else:strict_comparison=0
print_chapter=args.print_chapter[0]


print(args)

input_file='aeneas.csv'
df=(pd.read_csv(input_dir+'/'+input_file, encoding='utf-8')).astype(str)

target='verse_number'


if args.synced_silence: aeneas_adjusted_file='*_sync_adjusted.txt'
elif args.synced_qinfo:aeneas_adjusted_file='*_qinfo_adjusted.txt'
else:aeneas_adjusted_file='*_adjusted.txt'

#Get unique book and chapters
book_list=df['book'].unique()

try:
    for each_book in book_list:
        book_df=df.loc[df['book'] == each_book]

        chapter_list = book_df['chapter'].unique()

        if str(each_book).__contains__('HEB'):
            print(chapter_list)

        for each_chapter in chapter_list:

            #print('each_chapter->',each_chapter,'each_book->',each_book)
            if int(each_chapter)<10:
                chapter = '0'+each_chapter
            else:
                chapter=each_chapter


            book1 = each_book.replace(' ','')

            if (book1[0]).isdigit():
                book = book1[0] + (book1[1:]).capitalize()
            else:
                book = book1.capitalize()

            if book[1:] == 'Thessalonians': book = book[0] + 'Thess'

            book_find_string=chapter+'_'+book

            target_list = book_df[target][book_df['chapter'] == str(each_chapter)]
            uniq_target = (target_list.unique())[1:]



            aeneas_chapter_file = glob.glob(input_dir + '/*' +book_find_string + '*' + aeneas_adjusted_file)[0]

            file_name=(aeneas_chapter_file.split('/')[-1]).split('_sync_adjusted.txt')[0]

            if file_name.__contains__('Heb'):
                print(file_name)

            chapter=(re.split('\_+', file_name))[1]
            chap_book_match_string=('_'.join(re.split('_+',file_name)[1:3])).split(fileset_id_fix_string)[0]
            #print(chapter)
            sab_df=pd.read_csv(os.path.join(sys.path[0],'chapter_to_sab_mapping_n2.csv'))
            #print(sys.path[0],file_name)
            book_id=(sab_df[(sab_df.iloc[:, 0].str)           .contains(chap_book_match_string) == True].iloc[0,1])
            if len(sab_df[(sab_df.iloc[:, 0].str).contains(chap_book_match_string) == False])==0:
                print(file_name,chap_book_match_string,each_book)
            id = str(re.compile('\_+').split(file_name)[0])[1:]
            SAB_timing_filename = input_dir + '/' +'-'.join(['C01', id, book_id, chapter, 'timing.txt'])

            # Read cue info and aeneas for iteration in the foll. for loop
            aeneas_target = open(aeneas_chapter_file).readlines()

            ind = 0


            with open(SAB_timing_filename,'w') as sab:
                for each_target in uniq_target:
                    ind+=1


                    indices=[i for i,val in enumerate(target_list) if val==each_target]

                    #print(each_book,'|',each_chapter,'|',target_list,'|',each_target,indices)

                    aeneas_duration = 0

                    counter=0
                    aud_duration=0
                    aud_text=''

                    for each_index in indices:

                        aeneas_times = ((aeneas_target[each_index]).strip('\n')).split('\t')
                        aeneas_duration += float(aeneas_times[1]) - float(aeneas_times[0])
                        aud_duration=aeneas_duration
                        aud_text+=aeneas_times[-1][1:]

                        if counter==0:
                            aeneas_start=float(((aeneas_target[each_index]).strip('\n')).split('\t')[0])
                            aud_start=aeneas_start
                        counter+=1

                    sab.write(str(round(aud_start, 2)) + '\t' + str(     round(round(aud_start, 2) + round(aud_duration, 2),2)       ) + '\t' + str(each_target)+'\n')
except Exception as e:
    print(
        type(e).__name__,  # TypeError
        __file__,  # /tmp/example.py
        e.__traceback__.tb_lineno  # 2
    )





