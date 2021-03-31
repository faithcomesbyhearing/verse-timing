import pandas as pd,glob as gb,shutil as sh,os

test_dir='/Users/spanta/Documents/batch_aeneas_scripts/test_batch_scripts/'
audio_dir=test_dir+'audio/'
corescripts_dir=test_dir+'core_scripts/'
tmpdir=test_dir+'/tmp/'

core_df=pd.read_csv('/Users/spanta/Documents/batch_aeneas_scripts/get_core_script_stock_number_N2.csv',encoding='utf-8',index_col=None).astype(str)
fileset_df=pd.read_csv('/Users/spanta/Documents/batch_aeneas_scripts/get_stock_to_filesetID.csv',encoding='utf-8',index_col=None).astype(str)
query_result_df=pd.read_csv('/Users/spanta/Documents/batch_aeneas_scripts/query_result.csv',encoding='utf-8',index_col=None).astype(str)

merged1_df=pd.merge(core_df,fileset_df,on='stocknumber')
merged_df=pd.merge(merged1_df,query_result_df,on='filesetid')

for i,row in merged_df.iterrows():
    script=row['file_name']


    filesetid=str(row['filesetid'])
    tmp_location = os.path.join(tmpdir, filesetid)

    print(gb.glob(tmp_location+'/*sync*adj*.txt'),len(gb.glob(tmp_location+'/*sync*adj*.txt')))
    if len(gb.glob(tmp_location+'/*sync*adj*.txt'))==0:
        s3_dir=str(row['bibleid']).strip()

        if not os.path.isdir(os.path.join(corescripts_dir, filesetid)):
            os.mkdir(os.path.join(corescripts_dir, filesetid))


        print(script)

        sh.copy(gb.glob('/Users/spanta/Documents/batch_aeneas_scripts/batch_core_scripts/' + script)[0],
                os.path.join(corescripts_dir, filesetid))


        aws_execstring = 'aws s3 sync s3://dbp-prod/audio/' + s3_dir + '/' + filesetid + '/' + ' ' + os.path.join(audio_dir,
                                                                                                                  filesetid) + '/' + ' --exclude "*" --include "*B01*01*.mp3"'
        print(aws_execstring)
        os.system(aws_execstring)

        corescripts_location = os.path.join(corescripts_dir, filesetid, script)


        create_lines_from_corescript_execstring = 'python3 /Users/spanta/Desktop/adapted_for_batch/batch_create_lines_from_corescript_xls.py ' + \
                                                  ' -core_script ' + corescripts_location + \
                                                  ' -o ' + tmp_location + ' -book_chapter ' + '\'MAT 1\''
        print(create_lines_from_corescript_execstring)
        os.system(create_lines_from_corescript_execstring)

        lines_csv_location = os.path.join(tmp_location, 'lines.csv')
        input_audio_dir = os.path.join(audio_dir, filesetid)

        create_aeneas_execstring = 'python3 /Users/spanta/Desktop/adapted_for_batch/batch_new_create_aeneas.py ' \
                                   ' -input_lines_csv ' + lines_csv_location + \
                                   ' -input_audio_dir ' + input_audio_dir + \
                                   ' -output_dir ' + tmp_location + \
                                   ' -language_code epo ' \
                                   ' -input_book_to_audiobookid_mapfile /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/mapping_book_to_audiobookid.csv'
        os.system(create_aeneas_execstring)
