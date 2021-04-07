import pandas as pd, glob as gb, shutil as sh, os

test_dir = '/aeneas_test/aeneas_dirs/'
scripts_dir = '/aeneas_test/aeneas_scripts/'
audio_dir = test_dir + 'audio/'
corescripts_dir = test_dir + 'core_scripts/'
tmpdir = test_dir + '/aeneas_out/'
aeneas_timings_dir = test_dir + '/timings/'
qinfo_dir = test_dir + '/qinfo/'


def create_dirs(dir_list):
    for each_dir in dir_list:
        if not os.path.isdir(each_dir):
            os.mkdir(each_dir)


create_dirs([test_dir, audio_dir, corescripts_dir, tmpdir, aeneas_timings_dir, qinfo_dir])
# Files
book_to_audioid = scripts_dir + '/mapping_book_to_audiobookid.csv'

core_df = pd.read_csv(scripts_dir + '/get_core_script_stock_number_N2.csv', encoding='utf-8', index_col=None).astype(
    str)
core_df=core_df[core_df['script']!='NULL']

fileset_df = pd.read_csv(scripts_dir + '/get_stock_to_filesetID.csv', encoding='utf-8', index_col=None).astype(str)
fileset_df=fileset_df[fileset_df['script']!='NULL']

query_result_df = pd.read_csv(scripts_dir + '/query_result.csv', encoding='utf-8', index_col=None).astype(str)
query_result_df=query_result_df[query_result_df['script']!='NULL']


merged1_df = pd.merge(core_df, fileset_df, on='stocknumber')
merged_df = pd.merge(merged1_df, query_result_df, on='filesetid')

for i, row in merged_df.iterrows():
    script = row['file_name']

    filesetid = str(row['filesetid'])
    tmp_location = os.path.join(tmpdir, filesetid)

    stocknum = (str(row['stocknumber_x'])).replace('/', '')


    print(gb.glob(tmp_location + '/*sync*adj*.txt'), len(gb.glob(tmp_location + '/*sync*adj*.txt')))
    if len(gb.glob(tmp_location + '/*sync*adj*.txt')) == 0:
        s3_dir = str(row['bibleid']).strip()

        create_dirs([os.path.join(corescripts_dir, filesetid)])


        # sh.copy(gb.glob('/Users/spanta/Documents/batch_aeneas_scripts/batch_core_scripts/' + script)[0],
        #         os.path.join(corescripts_dir, filesetid))

        aws_execstring = 'aws s3 sync s3://dbp-prod/audio/' + s3_dir + '/' + filesetid + '/' + ' ' + os.path.join(
            audio_dir,
            filesetid) + '/' + ' --exclude "*" --include "*B01*01*.mp3"'
        print(aws_execstring)
        os.system(aws_execstring)

        corescripts_location = os.path.join(corescripts_dir, filesetid, script)

        extract_lines_from_corescript_execstring = 'python3 ' + scripts_dir + '/batch_create_lines_from_corescript_xls.py ' + \
                                                   ' -core_script ' + corescripts_location + \
                                                   ' -o ' + tmp_location + ' -book_chapter ' + '\'MAT 1\''
        print(extract_lines_from_corescript_execstring)
        os.system(extract_lines_from_corescript_execstring)

        lines_csv_location = os.path.join(tmp_location, 'lines.csv')
        input_audio_dir = os.path.join(audio_dir, filesetid)

        extract_aeneas_execstring = 'python3 ' + scripts_dir + '/batch_new_create_aeneas.py ' \
                                                               ' -input_lines_csv ' + lines_csv_location + \
                                    ' -input_audio_dir ' + input_audio_dir + \
                                    ' -output_dir ' + tmp_location + \
                                    ' -book_chapter ' + '\'MAT 1\''\
                                    ' -language_code epo ' \
                                    ' -input_book_to_audiobookid_mapfile ' + book_to_audioid
        os.system(extract_aeneas_execstring)

        create_dirs([os.path.join(aeneas_timings_dir, filesetid)])

        filesetid_timings_dir = aeneas_timings_dir + '/' + filesetid

        sab_line_timings_dir = filesetid_timings_dir + '/line_timings/'
        sab_verse_timings_dir = filesetid_timings_dir + '/verse_timings/'

        create_sab_string = 'python3 ' + scripts_dir + '/batch_create_sab_files.py ' \
                                                       ' -i ' + tmp_location + \
                            ' -o ' + sab_verse_timings_dir + \
                            ' -input_book_to_audiobookid_mapfile ' + book_to_audioid + \
                            ' -input_audio_dir ' + input_audio_dir

        print(create_sab_string)

        os.system(create_sab_string)

        create_sab_string = 'python3 ' + scripts_dir + '/batch_create_sab_files.py ' \
                                                       ' -i ' + tmp_location + \
                            ' -o ' + sab_line_timings_dir + \
                            ' -input_book_to_audiobookid_mapfile ' + book_to_audioid + \
                            ' -input_audio_dir ' + input_audio_dir + ' -extract_line_timing'

        os.system(create_sab_string)

        '''
        python3 /Users/spanta/Desktop/adapted_for_batch/batch_create_sab_files.py -i /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/tmp/BMQBSMN2DA/epo 
        -o /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/timings/BMQBSMN2DA/epo/line_timings 
        -input_book_to_audiobookid_mapfile /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/mapping_book_to_audiobookid.csv 
        -input_audio_dir /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/audio/BMQBSMN2DA -extract_line_timing
        '''

        #create_dirs([os.path.join(qinfo_dir, filesetid)])


        filesetid_qinfo_dir = os.path.join(qinfo_dir, stocknum, 'QINFO')
        print(filesetid_qinfo_dir)

        extract_line_from_clt_string = 'python3 ' + scripts_dir + '/batch_extract_cue_from_clt_file.py ' \
                                                                  ' -i ' + filesetid_qinfo_dir + \
                                       ' -o ' + tmp_location + \
                                       ' -input_book_to_audiobookid_mapfile ' + book_to_audioid + \
                                       ' -input_audio_dir ' + input_audio_dir
        os.system(extract_line_from_clt_string)

        '''
        python3 /Users/spanta/Desktop/adapted_for_batch/batch_extract_cue_from_clt_file.py -i /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/qinfo/BMQBSMN2DA 
        -o /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/tmp/BMQBSMN2DA 
        -input_book_to_audiobookid_mapfile /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/mapping_book_to_audiobookid.csv 
        -input_audio_dir /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/audio/BMQBSMN2DA
        '''

        filesetid_qc_dir = os.path.join(tmp_location, 'QC')
        create_dirs([filesetid_qc_dir])

        qc_string = 'python3 ' + scripts_dir + '/batch_QC.py ' \
                                               ' -cue_info_dir ' + tmp_location + \
                    ' -sab_timing_dir ' + sab_line_timings_dir + \
                    ' -aeneas_dir ' + tmp_location + \
                    ' -o ' + filesetid_qc_dir + \
                    ' -input_book_to_audiobookid_mapfile ' + book_to_audioid

        os.system(qc_string)

        '''
        python3 /Users/spanta/Desktop/adapted_for_batch/batch_QC.py -cue_info_dir /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/tmp/BMQBSMN2DA/eng 
        -sab_timing_dir /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/timings/BMQBSMN2DA/eng/line_timings 
        -aeneas_dir /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/tmp/BMQBSMN2DA/eng 
        -o /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/tmp/BMQBSMN2DA/eng/QC 
        -input_book_to_audiobookid_mapfile /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/mapping_book_to_audiobookid.csv
        '''

        os.system('rm -fr {}'.format(os.path.join(audio_dir, filesetid)))
        # os.rmdir(os.path.join(audio_dir, filesetid))