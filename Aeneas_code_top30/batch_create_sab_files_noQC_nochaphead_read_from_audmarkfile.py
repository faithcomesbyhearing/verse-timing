import pandas as pd,argparse,glob,statistics as stat,matplotlib.pyplot as plt,numpy as np,operator,re,sys,os,librosa as lb

parser = argparse.ArgumentParser(
        description='This function gives quality control metric between cue info and aeneas. Assumes only one book in aeneas.csv, assumes that each line in core script is translated'
                    'to cue info and aeneas, otherwise script fails')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input dir to find *sync_adjusted.txt aeneas output files')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output dir')
required_args.add_argument(
    '-input_audio_dir', required=True, nargs=1, type=str, help='Input directory that contains chapter audio mp3s')
required_args.add_argument(
    '-input_book_to_audiobookid_mapfile', required=True, nargs=1, type=str, help='Input file which contains mapping for book to audio book id')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-fileset_id_fix_string', nargs=1, type=str,default=['KO1SKVN2DA'],help='Mark if above check secs')
optional_args.add_argument('-strict_comparison', type=int,choices=[1,2], help='1-Compare aeneas and qinfo start boundaries. 2- Compare verse duration and 1')
optional_args.add_argument('-extract_line_timing', action='store_true', help='Compare verse timing info.')
optional_args.add_argument('-synced_silence', action='store_true', help='Indicate whether the output from aeneas timing was fully synced with silence adjustment')
optional_args.add_argument('-synced_qinfo', action='store_true', help='Indicate whether the output from aeneas timing was fully synced with qinfo')
optional_args.add_argument('-print_chapter', nargs=1, type=str,default=['9'],help='Print chapter')
optional_args.add_argument('-write_audition_format', action='store_true', help='Write output to audition tab csv format')
optional_args.add_argument('-check_secs', nargs=1, type=str,default=['3'],help='Mark if above check secs')

args = parser.parse_args()
input_dir=args.i[0]
output_dir=args.o[0]
book_to_audio_map=args.input_book_to_audiobookid_mapfile[0]
input_audio_dir=args.input_audio_dir[0]

fileset_id_fix_string=args.fileset_id_fix_string[0]

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

if args.strict_comparison is not None: strict_comparison=args.strict_comparison
else:strict_comparison=0
print_chapter=args.print_chapter[0]


print(args)

input_file=os.path.join(input_dir,'aeneas.csv')
df=(pd.read_csv(input_file, encoding='utf-8')).astype(str)

target='verse_number'

if args.extract_line_timing:target='line_number'

aeneas_adjusted_file='_audition_markers.csv'

#Get unique book and chapters
book_list=df['book'].drop_duplicates()

print(book_list.to_string(index=False))
# try:
for each_book in book_list:
    book_df=df.loc[df['book'] == each_book]

    chapter_list = book_df['chapter'].unique()

    if str(each_book).__contains__('HEB'):
        print(chapter_list)

    for each_chapter in chapter_list:

        print('each_chapter->',each_chapter,'each_book->',each_book)
        if int(each_chapter)<10:
            chapter = '0'+each_chapter
        else:
            chapter=each_chapter


        book1 = each_book.replace(' ','')

        if (book1[0]).isdigit():
            book = book1[0] + (book1[1:])
        else:
            book = book1

        print('book',book)

        if book[1:] == 'Thessalonians': book = book[0] + 'Thess'

        map_book_df=pd.read_csv(book_to_audio_map)
        #print(sys.path[0],file_name)
        audio_book_id=(map_book_df[(map_book_df.iloc[:, 2].str)           .contains(book) == True].iloc[0,1])

        if int(audio_book_id)<10:
            audio_book_id='0'+str(audio_book_id)
        else:
            audio_book_id=str(audio_book_id)

        book_find_string = audio_book_id + '*' + chapter

        mp3_string='/*'+audio_book_id+'*'+chapter+'*.mp3'
        chapter_length=lb.get_duration(
            filename=glob.glob(input_audio_dir+mp3_string)[0])

        print('book_find_string',book_find_string)

        target_list = book_df[target][book_df['chapter'] == str(each_chapter)]

        if args.extract_line_timing:
            uniq_target = (target_list.unique())
        else:
            uniq_target = (target_list.unique())[1:]



        aeneas_chapter_file = glob.glob(input_dir + '/*' +book_find_string + '*' + aeneas_adjusted_file)[0]

        file_name=(aeneas_chapter_file.split('/')[-1]).split(aeneas_adjusted_file)[0]

        if file_name.__contains__('Heb'):
            print(file_name)

        chapter=(re.split('\_+', file_name))[1]
        chap_book_match_string=('_'.join(re.split('_+',file_name)[1:3])).split(fileset_id_fix_string)[0]
        sab_df=pd.read_csv(book_to_audio_map)
        each_book=str(each_book).strip()
        book_id=(sab_df[(sab_df.iloc[:, 2].str)           .contains(each_book) == True].iloc[0,2])
        if len(sab_df[(sab_df.iloc[:, 0].str).contains(chap_book_match_string) == False])==0:
            print(file_name,chap_book_match_string,each_book)
        id = str(re.compile('\_+').split(file_name)[0])[1:]
        SAB_timing_filename = output_dir + '/' +'-'.join(['C01', id, book_id, chapter, 'timing.txt'])
        print(SAB_timing_filename)

        # Read cue info and aeneas for iteration in the foll. for loop
        aeneas_target = open(aeneas_chapter_file).readlines()[1:]

        ind = 0

        aud_df = pd.read_csv(aeneas_chapter_file,sep="\t")


        target_list=aud_df['Name'].unique()
        uniq_target=target_list

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
                    print(each_target,each_index)

                    atime = (aeneas_target[each_index]).split('\t')[1:3]
                    #print(atime)
                    aeneas_times=list()
                    aeneas_times.append(float((atime[0]).split(':')[1]))
                    aeneas_times.append(float((atime[1]).split(':')[1])+float((atime[0]).split(':')[1]))

                    aeneas_duration += float(aeneas_times[1]) - float(aeneas_times[0])
                    aud_duration = aeneas_duration

                    if counter == 0:
                        aeneas_start = float(aeneas_times[0])
                        aud_start = aeneas_start
                    counter += 1
                if ind!=len(uniq_target):
                    sab.write(str(round(aud_start, 2)) + '\t' + str(round(round(aud_start, 2) + round(aud_duration, 2), 2)) + '\t' + str(each_target).split('_')[2] + '\n')
                else:
                    sab.write(str(round(aud_start, 2)) + '\t' + str(      round(chapter_length,2) ) + '\t' + str(each_target).split('_')[2] + '\n')


                #sab.write(str(round(aeneas_start, 2)) + '\t' + str(     round(round(aeneas_start, 2) + round(aeneas_duration, 2),2)       ) + '\t' + str(each_target)+'\n')
# except Exception as e:
#     print(
#         type(e).__name__,  # TypeError
#         __file__,  # /tmp/example.py
#         e.__traceback__.tb_lineno  # 2
#     )
#
