import argparse,re,pandas as pd,os,csv,glob,codecs,shutil,sys
from num2words import num2words
from langdetect import detect
from pydub import AudioSegment

parser = argparse.ArgumentParser(
        description='This function creates lines.csv file from core script .xls file. Assumes lines.csv has header')
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
optional_args.add_argument('-sound_find_string', nargs=1, type=str,help='EX: MRK to get MRK1,ESV_MRK_01 etc.')
optional_args.add_argument('-book_chapter', nargs=1, type=str, default=['MATTHEW 1'],help='custom book chapter. Be sure to include the space. EX: John 9')
optional_args.add_argument('-noheader', action='store_true', help='Remove header: fileset,book,chapter,line#,verse#,verse_content,time')
optional_args.add_argument('-no_audacity_output', action='store_true', help='Remove header: fileset,book,chapter,line#,verse#,verse_content,time')
optional_args.add_argument('-input_no_header', action='store_true', help='Indicate whether input lines.csv has header or not')
optional_args.add_argument('-adjust_silence', action='store_true', help='Adjust boundaries with closest silence midpoint')
optional_args.add_argument('-move_adjustment', action='store_true', help='Move time points as you adjust for silence')
optional_args.add_argument('-write_audition_format', action='store_true', help='Write output to audition tab csv format')


args = parser.parse_args()
print(args)

input_file=args.input_lines_csv[0]
input_audio_dir=args.input_audio_dir[0]
output_dir=args.output_dir[0]
language_code=args.language_code[0]
sound_find_string=None
if args.sound_find_string is not None: sound_find_string=args.sound_find_string[0]

file_name='aeneas.csv'
output_file=os.path.join(output_dir,file_name)
write_file_handle=open(output_file,'a+',encoding='utf-8')
write_file = csv.writer(write_file_handle)

# Write header as requested by user
if not(args.noheader):write_file.writerow(('fileset','book','chapter','line_number', 'verse_number','verse_content','time'))


book_chapter_list=list()
def get_chapters_index(df):
    current_book_chapter=df['book'][0]+'_'+'0'+df['chapter'][0]
    book_chapter_list.append((str(df['book'][0]).replace(" ", "") + '_' + '0' + df['chapter'][0]).replace(' ', '_'))
    for i in range(1,len(df)):
        if df['book'][i]!=current_book_chapter.split('_')[0] or df['chapter'][i]!=(current_book_chapter.split('_')[1]).lstrip('0'):
            if int(df['chapter'][i])<10:
                current_book_chapter=str(df['book'][i]).replace(" ", "")+'_'+df['chapter'][i]

                book_chapter_list.append((    str(df['book'][i]).replace(" ", "")            +'_'+'0'+df['chapter'][i]).replace(' ','_'))
            else:
                current_book_chapter = str(df['book'][i]).replace(" ", "") + '_' + df['chapter'][i]
                book_chapter_list.append((current_book_chapter).replace(' ','_'))
    return  list(set(book_chapter_list))

input_df=(pd.read_csv(input_file, encoding='utf-8')).astype(str)
if args.book_chapter is not None:book_chapter=[args.book_chapter[0]]
book_chapter_list=get_chapters_index(input_df)
print(book_chapter_list)


missing_chapters=list()
def create_aeneas_csv(df=input_df,book_chapter_list=book_chapter_list,input_audio_dir=input_audio_dir):

    try:
        for each_chapter in book_chapter_list:

            search_book = each_chapter.split('_')[0]
            chapter=each_chapter.split('_')[1]
            book1=each_chapter.split('_')[0]

            if (book1[0]).isdigit():
                book=book1[0]+(book1[1:]).capitalize()
            else:
                book=book1.capitalize()
            if each_chapter.split('_')[0][1:] == 'THESSALONIANS': book = each_chapter.split('_')[0][0]+'Thess'


            find_audio_string = chapter + '_' + book
            if sound_find_string is not None:
                find_audio_string = chapter+'_' + sound_find_string
                if language_code == 'en':find_audio_string=chapter+'_'+sound_find_string

            #print(find_audio_string)
            chapter_audio=glob.glob(input_audio_dir+'/*'+find_audio_string+'*')[0]
            if not(chapter_audio):missing_chapters.append(each_chapter)

            #Create aeneas text input
            aeneas_file_name=(chapter_audio.split('/')[-1]).split('.')[0]+'_aeneas_input.txt'
            aeneas_write=codecs.open(output_dir+'/'+aeneas_file_name, 'w', 'utf-8')
            chapter=chapter.lstrip('0')

            for i in range(0,len(df)):
                if (      ((str(df['book'][i])).strip()      ).upper()).replace(' ','')  ==search_book.upper() and int(df['chapter'][i])==int(chapter):
                    aeneas_write.write(df['verse_content'][i]+'\n')
            aeneas_write.close()

            #Run aeneas
            from aeneas.executetask import ExecuteTask
            from aeneas.task import Task
            from aeneas.tools.execute_task import ExecuteTaskCLI

            # create Task object
            aeneas_output_file=(chapter_audio.split('/')[-1]).split('.')[0]+'_aeneas_out.txt'

            if find_audio_string=='01_Matthew':
                config_string = u"is_audio_file_head_length=22|task_adjust_boundary_percent_value=50|task_adjust_boundary_nonspeech_min=0.4|task_language=dan|is_text_type=plain|os_task_file_format=aud"
            else:
                config_string = u"task_adjust_boundary_percent_value=50|task_adjust_boundary_nonspeech_min=0.4|task_language=dan|is_text_type=plain|os_task_file_format=aud"

            #print(config_string)
            check_file=os.path.join (output_dir,    (chapter_audio.split('/')[-1]).split('.')[0]+'_sync_adjusted.txt')



            if not os.path.isfile(check_file):
                print(os.path.isfile(check_file),check_file)
                print(os.path.join(output_dir, aeneas_output_file))
                #Save .txt file
                ExecuteTaskCLI(use_sys=False).run(arguments=[
                    None,  # dummy program name argument
                    chapter_audio,
                    os.path.join(output_dir,aeneas_file_name),
                    config_string,
                    os.path.join(output_dir,aeneas_output_file)
                ])

                # # Save time boundary
                task = Task(config_string=config_string)
                task.audio_file_path_absolute = chapter_audio
                print(aeneas_file_name)
                task.text_file_path_absolute = os.path.join(output_dir,aeneas_file_name)
                task.sync_map_file_path_absolute=os.path.join(output_dir,aeneas_output_file)


                # #process Task
                ExecuteTask(task).execute()

                index_list = list()

                with open(output_dir+'/'+aeneas_output_file,'r') as a:
                    with open(output_dir + '/' + 'new' + aeneas_output_file, 'w') as b:
                        for line in a:
                            if not(line.__contains__('......')):

                                b.write(line)
                a.close()
                b.close()

                shutil.move(output_dir+'/new'+aeneas_output_file,output_dir+'/'+aeneas_output_file)


                last=len(task.sync_map_leaves())
                for i,time in enumerate(task.sync_map_leaves()):
                    if 0<i<last-1:
                        index_list.append(time.end)



                inc=0
                verse_list=list()
                for i in range(0, len(df)):
                    if (      ((str(df['book'][i])).strip() ).replace(' ','')     ).upper() == search_book.upper() and int(df['chapter'][i])==int(chapter):
                        write_file.writerow((df['fileset'][i],df['book'][i],df['chapter'][i],df['line_number'][i],df['verse_number'][i],df['verse_content'][i],index_list[inc]))
                        verse_list.append(df['verse_number'][i])
                        inc+=1

                print(chapter_audio)

                if args.move_adjustment:
                    silence_file = output_dir + '/' + (aeneas_output_file.split('/')[-1]).split('.')[0] + '_silence.txt'
                    extract_silence_intervals(chapter_audio, silence_file)
                    sound = AudioSegment.from_mp3(chapter_audio)
                    framerate=sound.frame_rate

                    print(verse_list)
                    adjust_update_boundaries_with_silence(output_dir + '/' + aeneas_output_file, silence_file,
                                                   output_dir + '/' + (chapter_audio.split('/')[-1]).split('.')[
                                                       0] + '_sync_adjusted.txt', verse_list,framerate,input_split_field='\t', output_split_field='\t')

                elif args.adjust_silence:
                    silence_file=output_dir+'/'+(aeneas_output_file.split('/')[-1]).split('.')[0]+'_silence.txt'
                    extract_silence_intervals(chapter_audio,silence_file)
                    adjust_boundaries_with_silence(output_dir+'/'+aeneas_output_file,silence_file,output_dir+'/'+(chapter_audio.split('/')[-1]).split('.')[0]+'_adjusted.txt',
                                                   verse_list,
                                                   input_split_field='\t',output_split_field='\t')

        write_file_handle.close()

        if missing_chapters:
            with open(output_dir + '/missing_chapters.txt', 'w', encoding='utf-8') as missing:
                for each_missing in missing_chapters:
                    missing.write(each_missing)
                missing.close()
    except Exception as err:
        print(
            type(e).__name__,  # TypeError
            __file__,  # /tmp/example.py
            e.__traceback__.tb_lineno  # 2
        )

#new silence 8 min silence 400
def extract_silence_intervals(input_file,output_file,decibels=5,min_sil_len=400):
    import pydub.silence as sil, os, re

    # Open the write file
    if os.path.exists(output_file): os.remove(output_file)
    write_file = open(output_file, 'w')

    if input_file.split('.')[-1]=='mp3':
        sound=AudioSegment.from_mp3(input_file)
    else:
        sound = AudioSegment.from_wav(input_file)


    dBFS = sound.dBFS
    print('decibels',dBFS)
    silence_boundaries = sil.detect_silence(sound, min_silence_len=min_sil_len, silence_thresh=dBFS - decibels)

    for boundaries in silence_boundaries:
        boundaries = [x / 1000 for x in boundaries]
        write_file.write("{0},{1}\n".format(boundaries[0], boundaries[1]))
    write_file.close()



def adjust_boundaries_with_silence(input_file,silence_file,output_file,verse_list,input_split_field=',',silence_split_field=',',output_split_field=','):
    #This function adjusts the boundaries of input file with silence mid points
    inc=0
    new0=list()
    with open(input_file,'r') as f:
        with open(output_file,'w') as up:
            #Read input file
            for line in f:
                line=line.replace('\n','')
                adjust_boundary0=float(line.split(input_split_field)[0])
                adjust_boundary1 = float(line.split(input_split_field)[1])
                # if len(line.split(input_split_field))>2: text=output_split_field+line.split(input_split_field)[2]
                if len(line.split(input_split_field)) > 2:
                    text =line.split(input_split_field)[2]
                else:text=''
                inc += 1

                #Read silence file
                with open(silence_file,'r') as s:
                    for silence_bounds in s:
                        silence_start=float(silence_bounds.split(silence_split_field)[0])
                        silence_end=float(silence_bounds.split(silence_split_field)[1])

                        #if boundary falls inside silence, move it to silence region mid point
                        if (silence_start<=adjust_boundary1<=silence_end) or ( (abs(silence_start - adjust_boundary1) <= 0.3 or abs(
                                silence_end - adjust_boundary1) <= 0.3) and (silence_start - silence_end) )>= 0.4:
                            adjust_boundary1=(silence_start+silence_end)/2
                            break
                s.close()
                new0.append(adjust_boundary1)
                #Write to output file
                if inc==1:up.write(str(round(adjust_boundary0,3))+output_split_field+str(round(adjust_boundary1,3))+output_split_field+str(verse_list[inc-1])+text+'\n')
                else:up.write(str(round(new0[inc-2],3))+output_split_field+str(round(adjust_boundary1,3))+output_split_field+str(verse_list[inc-1])+text+'\n')
        up.close()
    f.close()


def adjust_update_boundaries_with_silence(input_file,silence_file,output_file,verse_list,framerate,input_split_field=',',silence_split_field=',',output_split_field=','):
    #This function adjusts the boundaries of input file with silence mid points and pulls the rest of the verse timings by the adjusted time
    inc=0
    new0=list()

    move_time=0
    if args.write_audition_format:
        audition_file_name = (output_file.split('/')[-1]).split('_sync_adjusted.txt')[0] + '_audition_markers.csv'
        audition_file = output_dir + '/' + audition_file_name
        marker_name='A_Marker_'
    with open(input_file,'r') as f:
        with open(audition_file, 'w') as aud:
            with open(output_file,'w') as up:

                    #Read input file
                    for line in f:
                        line=line.replace('\n','')
                        adjust_boundary0=float(line.split(input_split_field)[0])
                        adjust_boundary1 = float(line.split(input_split_field)[1])+move_time
                        if len(line.split(input_split_field)) > 2:
                            text =line.split(input_split_field)[2]
                        else:text=''
                        inc += 1

                        #Read silence file
                        with open(silence_file,'r') as s:
                            for silence_bounds in s:
                                silence_start=float(silence_bounds.split(silence_split_field)[0])
                                silence_end=float(silence_bounds.split(silence_split_field)[1])

                                if (silence_start - silence_end) >= 0.4:
                                    print(silence_start,silence_end)

                                if (silence_start <= adjust_boundary1 <= silence_end) or (
                                        (abs(silence_start - adjust_boundary1) <= 0.3 or abs(
                                                silence_end - adjust_boundary1) <= 0.3) and (
                                                silence_start - silence_end)) >= 0.4:
                                    adjust_boundary1 = (silence_start + silence_end) / 2
                                    move_time += ((silence_start + silence_end) / 2) - adjust_boundary1
                                    break
                        s.close()
                        new0.append(adjust_boundary1)
                        #Write to output file
                        if inc==1:
                            print('yes1')
                            up.write(str(round(adjust_boundary0,3))+output_split_field+str(round(adjust_boundary1,3))+output_split_field+str(verse_list[inc-1])+text+'\n')

                            aud.write(
                                'Name' + '\t' + 'Start' + '\t' + 'Duration' + '\t' + 'Time Format' + '\t' + 'Type' + '\t' + 'Description' + '\n')

                            aud.write(marker_name + str(verse_list[inc - 1]) + '\t' + '0:' + str(adjust_boundary0) + '\t' + '0:' + str(adjust_boundary1 - adjust_boundary0) + '\t'
                                      + 'decimal' + '\t' + 'Cue' + '\t' + str(verse_list[inc - 1]) + text + '\n')


                        else:
                            print('yes')
                            up.write(str(round(new0[inc-2],3))+output_split_field+str(round(adjust_boundary1,3))+output_split_field+str(verse_list[inc-1])+text+'\n')

                            aud.write(marker_name + str(verse_list[inc - 1]) + '\t' + '0:' + str((new0[inc - 2])) + '\t' + '0:' + str(adjust_boundary1 - new0[inc - 2]) + '\t'
                                      + 'decimal' + '\t' + 'Cue' + '\t' + str(verse_list[inc - 1]) + text + '\n')

        aud.close()

        up.close()
    f.close()


create_aeneas_csv()

