
''' This function reads a core script and print line and verse info. of target language

EX run:
python3 create_aeneas.py -input_lines_csv /Users/spanta/Desktop/jon_code_test/upload_code/telugu_lines.csv -input_audio_dir /telugu_64_non_drama -o /telugu_aeneas -language_code eng
'''



import argparse,re,pandas as pd,os,csv,glob,codecs
from num2words import num2words
from langdetect import detect


parser = argparse.ArgumentParser(
        description='This function creates lines.csv file from core script .xls file')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-input_lines_csv', required=True, nargs=1, type=str, help='Input excel which contains lines.csv')
required_args.add_argument(
    '-input_audio_dir', required=True, nargs=1, type=str, help='Input directory that contains chapter audio mp3s')
required_args.add_argument(
    '-output_dir', required=True, nargs=1, type=str, help='Output directory to store aeneas.csv files')
required_args.add_argument(
    '-language_code', required=True, nargs=1, type=str, help='3 letter Language code to use for aeneas')


optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-book_chapter', nargs=1, type=str, default=['MATTHEW 1'],help='custom book chapter. Be sure to include the space. EX: John 9')
optional_args.add_argument('-noheader', action='store_true', help='Remove header: fileset,book,chapter,line#,verse#,verse_content,time')
optional_args.add_argument('-no_audacity_output', action='store_true', help='Remove header: fileset,book,chapter,line#,verse#,verse_content,time')
optional_args.add_argument('-input_no_header', action='store_true', help='Indicate whether input lines.csv has header or not')

args = parser.parse_args()
print(args)

input_file=args.input_lines_csv[0]
input_audio_dir=args.input_audio_dir[0]
output_dir=args.output_dir[0]
language_code=args.language_code[0]




file_name='aeneas.csv'
output_file=os.path.join(output_dir,file_name)
write_file_handle=open(output_file,'w',encoding='utf-8')
write_file = csv.writer(write_file_handle)
# Write header as requested by user
if not(args.noheader):write_file.writerow(('fileset','book','chapter','line_number', 'verse_number','verse_content','time'))


book_chapter_list=list()
def get_chapters_index(df):
    current_book_chapter=df['book'][0]+'_'+'0'+df['chapter'][0]
    book_chapter_list.append(df['book'][0]+'_'+'0'+df['chapter'][0])

    for i in range(1,len(df)):
        if df['book'][i]!=current_book_chapter.split('_')[0] or df['chapter'][i]!=(current_book_chapter.split('_')[1]).lstrip('0'):
            if int(df['chapter'][i])<10:
                current_book_chapter=df['book'][i]+'_'+df['chapter'][i]

                book_chapter_list.append((df['book'][i]+'_'+'0'+df['chapter'][i]).replace(' ','_'))
            else:
                current_book_chapter = df['book'][i] + '_' + df['chapter'][i]
                book_chapter_list.append((current_book_chapter).replace(' ','_'))
    return  book_chapter_list

input_df=(pd.read_csv(input_file, encoding='utf-8')).astype(str)
if args.book_chapter is not None:book_chapter=[args.book_chapter[0]]
book_chapter_list=get_chapters_index(input_df)
print(book_chapter_list)


missing_chapters=list()

def create_aeneas_csv(df=input_df,book_chapter_list=book_chapter_list,input_audio_dir=input_audio_dir):
    for each_chapter in book_chapter_list:

        #Find respective mp3 file
        if len(each_chapter.split('_'))==3:
            sequence=re.findall(r'\d+', each_chapter.split('_')[0])[0]

            if each_chapter.split('_')[1]=='THESSALONIANS':book='Thess'
            else:book=(each_chapter.split('_')[1]).capitalize()

            chapter=each_chapter.split('_')[2]
            find_mp3_string=chapter+'_'+sequence+book

            search_book = ' '.join(each_chapter.split('_')[0:2])
        else:
            if each_chapter.split('_')[1]=='THESSALONIANS':book='Thess'
            else:
                book=(each_chapter.split('_')[0]).capitalize()
                search_book=each_chapter.split('_')[0]

            chapter = each_chapter.split('_')[1]
            find_mp3_string = chapter + '_' +book
        chapter_mp3=glob.glob(input_audio_dir+'/*'+find_mp3_string+'*')[0]
        if not(chapter_mp3):missing_chapters.append(each_chapter)


        #Create aeneas text input
        aeneas_file_name=(chapter_mp3.split('/')[-1]).split('.')[0]+'_aeneas_input.txt'
        aeneas_write=codecs.open(output_dir+'/'+aeneas_file_name, 'w', 'utf-8')
        chapter=chapter.lstrip('0')



        for i in range(0,len(df)):
            if (      (str(df['book'][i])).strip()      ).upper()==search_book.upper() and int(df['chapter'][i])==int(chapter):
                aeneas_write.write(df['verse_content'][i]+'\n')
        aeneas_write.close()

        #Run aeneas
        from aeneas.executetask import ExecuteTask
        from aeneas.task import Task
        from aeneas.tools.execute_task import ExecuteTaskCLI



        # create Task object
        aeneas_output_file=(chapter_mp3.split('/')[-1]).split('.')[0]+'_aeneas_out.aud'
        config_string = f"task_language={language_code}|is_text_type=plain|os_task_file_format=aud"

        # Save .aud file
        ExecuteTaskCLI(use_sys=False).run(arguments=[
            None,  # dummy program name argument
            chapter_mp3,
            os.path.join(output_dir,aeneas_file_name),
            config_string,
            os.path.join(output_dir,aeneas_output_file)
        ])

        # Save time boundary
        task = Task(config_string=config_string)
        task.audio_file_path_absolute = chapter_mp3
        task.text_file_path_absolute = os.path.join(output_dir,aeneas_file_name)
        task.sync_map_file_path_absolute=os.path.join(output_dir,aeneas_output_file)

        index_list=list()
        # process Task
        ExecuteTask(task).execute()
        last=len(task.sync_map_leaves())
        for i,time in enumerate(task.sync_map_leaves()):
            if 0<i<last-1:
                index_list.append(time.end)
                # print(time.end)


        inc=0
        for i in range(0, len(df)):
            if (      (str(df['book'][i])).strip()      ).upper() == search_book.upper() and int(df['chapter'][i])==int(chapter):
                write_file.writerow((df['fileset'][i],df['book'][i],df['chapter'][i],df['line_number'][i],df['verse_number'][i],df['verse_content'][i],index_list[inc]))
                inc+=1

        print(chapter_mp3)
    write_file_handle.close()

    if missing_chapters:
        with open(output_dir + '/missing_chapters.txt', 'w', encoding='utf-8') as missing:
            for each_missing in missing_chapters:
                missing.write(each_missing)
            missing.close()


create_aeneas_csv()

