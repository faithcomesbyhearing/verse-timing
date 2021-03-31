import argparse,re,glob,os
import pandas as pd,librosa as lb

parser = argparse.ArgumentParser(
        description='This function creates cue.csv file from clt file')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input dir of .clt files')
required_args.add_argument(
    '-input_book_to_audiobookid_mapfile', required=True, nargs=1, type=str, help='Input file which contains mapping for book to audio book id')
required_args.add_argument(
    '-input_audio_dir', required=True, nargs=1, type=str, help='Input directory that contains chapter audio mp3s')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output dir to store cue info text files')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-fileset', nargs=1, type=str,help='custom fileset id')
optional_args.add_argument('-book', nargs=1, type=str, help='custom book id')
optional_args.add_argument('-chapter', nargs=1, type=str,help='custom chapter id')
optional_args.add_argument('-noheader', action='store_true', help='Remove header: fileset,book,chapter,db,sId,sBegin,sEnd')

args = parser.parse_args()
input_dir=args.i[0]
book_to_audio_map=args.input_book_to_audiobookid_mapfile[0]
output_dir=args.o[0]
input_audio_dir=args.input_audio_dir[0]


if len(glob.glob(input_dir+'/*manual*timings*'))!=0:

    df = pd.read_csv(glob.glob(input_dir + '/*manual*timings*')[0],
                     index_col=False)

    if str(df.columns).__contains__('osis_code'):



        for index, row in df.iterrows():

            book_id = str(df['book_id'][index])


            map_book_df = pd.read_csv(book_to_audio_map)
            print(book_id)
            audio_book_id = (map_book_df[(map_book_df.iloc[:, 0].str).contains(book_id) == True].iloc[0, 1])

            if int(audio_book_id) < 10:
                audio_book_id = '0' + str(audio_book_id)
            else:
                audio_book_id = str(audio_book_id)

            id=audio_book_id

            chapter = int(df['chapter_start'][index])
            if chapter < 10:
                chapter = '0' + str(chapter)
            else:
                chapter = str(chapter)

            mp3_string='/*'+audio_book_id+'*'+chapter+'*.mp3'
            chapter_length=lb.get_duration(
                filename=glob.glob(input_audio_dir+mp3_string)[0])
            print(chapter_length)

            SAB_timing_filename = '_'.join(['C01', id, book_id, chapter, '_cue_info.txt'])
            if index != size - 1:
                if df['chapter_start'][index] == df['chapter_start'][index + 1]:
                    with open(output_dir + '/' + SAB_timing_filename, 'a') as sab:
                        sab.write('\t'.join([str(  round(df['timestamp'][index] ,3)), str(    round(df['timestamp'][index + 1] ,3)          ),
                                             str(       df['verse_start'][index]            )]) + "\n")
                    sab.close()
                elif (df['chapter_start'][index] != df['chapter_start'][index + 1]):
                    with open(output_dir + '/' + SAB_timing_filename, 'a') as sab:
                        sab.write('\t'.join([str(      round(df['timestamp'][index] ,3)        ), str(      round(chapter_length,2) ),
                                             str( df['verse_start'][index]            )]))
                    sab.close()
            else:
                with open(output_dir + '/' + SAB_timing_filename, 'a') as sab:
                    sab.write('\t'.join([str(   round(df['timestamp'][index] ,3)         ),str(      round(chapter_length,2) ),
                                         str(               df['verse_start'][index]                )]))
                sab.close()
    else:
        for index, row in df.iterrows():
            file_name = str(df['file_name'][index])
            book_id = str(df['book_id'][index])
            id = str(re.compile('\_+').split(file_name)[0])[1:]
            # id=file_name.split('_')[0]
            # chapter=file_name.split('___')[0]
            # chapter=re.compile('\_+').split(file_name)[1]
            chapter = int(df['chapter_start'][index])
            if chapter < 10:
                chapter = '0' + str(chapter)
            else:
                chapter = str(chapter)
            SAB_timing_filename = '-'.join(['C01', id, book_id, chapter, '_cue_info.txt'])
            if index != size - 1:
                if df['file_name'][index] == df['file_name'][index + 1]:
                    with open(dir + '/' + SAB_timing_filename, 'a') as sab:
                        sab.write('\t'.join([str(df['timestamp'][index]), str(df['timestamp'][index + 1]),
                                             str(df['verse_start'][index])]) + "\n")
                    sab.close()
                elif (df['file_name'][index] != df['file_name'][index + 1]):
                    with open(dir + '/' + SAB_timing_filename, 'a') as sab:
                        sab.write('\t'.join(
                            [str(df['timestamp'][index]), str(round(float(df['chapter_length'][index]), 2)),
                             str(int(df['verse_start'][index]))]))
                    sab.close()
            else:
                with open(dir + '/' + SAB_timing_filename, 'a') as sab:
                    sab.write('\t'.join([str(df['timestamp'][index]), str(round(float(df['chapter_length'][index]), 2)),
                                         str(df['verse_start'][index])]))
                sab.close()

elif len(glob.glob(input_dir+'/*.clt')) !=0 :
    for input_file in glob.glob(input_dir+'/*.clt'):

        print(input_file)

        # Open read and write files
        read_file=open(input_file,'r')
        out_file_name=(input_file.split('/')[-1]).split('_VOX')[0]+'_cue_info.txt'
        write_file=open(os.path.join(output_dir,out_file_name),'w')



        #Fill the header values and overwrite custom option
        filename=input_file.split('/')[-1]
        input=re.compile('\_+').split(filename.split('.')[0])
        if args.fileset is not None:file_setid=args.fileset[0]
        else:file_setid=input[1]+input[0]
        if args.book is not None: book_name=args.book[0]
        else:book_name=input[-2]
        if args.chapter is not None:chapter_num=args.chapter[0]
        else:chapter_num=input[-3]

        # Adjust decoding patterm in .clt
        lines=read_file.readlines()
        bits_per_second=float((lines[2]).strip())

        start_time_id=3
        duration_id=4
        line_number_id=5
        increment=5
        '''IMPL the cues in core script are recorded in the clt as cue 01 for mat 24
        In core script it says +2 secs, its duration in clt is 1.66 secs'''

        while line_number_id<=len(lines):

            start_time=round(float(lines[start_time_id].strip())/bits_per_second,3)
            end_time=round( (float(lines[start_time_id].strip()) +float(lines[duration_id].strip()) ) /bits_per_second,3)
            line_audio_file = (lines[line_number_id]).strip()
            line_number=(re.compile('\_+').split(line_audio_file.split('.')[0]))[-1]
            if line_number.__contains__('ue')==False:
                print(input_file)
                write_file.write(str(start_time)+'\t'+str(end_time)+'\t'+str(line_number)+'\n')
            start_time_id+=increment
            duration_id += increment
            line_number_id+=increment

        read_file.close()
        write_file.close()

