import pandas as pd, glob as gb, shutil as sh, os, time,shutil
import argparse
import subprocess as subp

parser = argparse.ArgumentParser(
        description='This function creates lines.csv file from core script .xls file. Assumes lines.csv has header')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-input_file', required=True, nargs=1, type=str, help='input batch_file ')


args = parser.parse_args()
input_file=args.input_file[0]


def create_dirs(dir_list):
    for each_dir in dir_list:
        if not os.path.isdir(each_dir):
            os.mkdir(each_dir)

def run_aeneas():
    start_time = time.time()
    test_dir = '/home/ubuntu/aeneas_test/aeneas_dirs/'
    scripts_dir = '/home/ubuntu/aeneas_test/aeneas_scripts/'
    audio_dir = test_dir + 'audio/'
    corescripts_dir = test_dir + 'core_scripts/'
    tmpdir = test_dir + '/aeneas_out/'
    aeneas_timings_dir = test_dir + '/timings/'
    verse_timings_dir = test_dir + '/top30_N2/'
    qinfo_dir = test_dir + '/qinfo/'

    os.system('rm -fr '+audio_dir+'/*')
    create_dirs([test_dir, audio_dir, tmpdir, aeneas_timings_dir,verse_timings_dir,verse_timings_dir+'/pass_qc/',verse_timings_dir+'/failed_qc/',verse_timings_dir+'/other/'])
    # Files
    book_to_audioid = scripts_dir + '/mapping_book_to_audiobookid.csv'

    core_df = pd.read_csv(scripts_dir + '/'+input_file, encoding='utf-8',
                          index_col=None).astype(str)

    # core_df = pd.read_csv(scripts_dir + '/1get_core_script_stock_number_N2.csv', encoding='utf-8',index_col=None).astype(str)

    core_df = core_df[core_df['script'] != 'NULL']

    #fileset_df = pd.read_csv(scripts_dir + '/get_stock_to_filesetID_N2.csv', encoding='utf-8', index_col=None).astype(str)
    #fileset_df = fileset_df[fileset_df['script'] != 'NULL']

    #query_result_df = pd.read_csv(scripts_dir + '/query_result_N2.csv', encoding='utf-8', index_col=None).astype(str)
    #query_result_df = query_result_df[query_result_df['script'] != 'NULL']

    #merged1_df = pd.merge(core_df, fileset_df, on='stocknumber')
    #merged1_df=merged1_df.rename(columns={"filesetid_x": "filesetid"})
    #merged_df = pd.merge(merged1_df, query_result_df, on='filesetid')
    #merged1_df=merged1_df.rename(columns={"bibleid_x": "bibleid"})



    for i, row in core_df.iterrows():
        print(row,row['file_name'])
        script = row['file_name']

        filesetid = str(row['filesetid'])
        #filesetid="PORARAN2DA"
        tmp_location = os.path.join(tmpdir, filesetid)

        stocknum = (str(row['stocknumber'])).replace('/', '')
        #stocknum=stocknum.replace('N1','N2')
        filesetid_qinfo_dir = os.path.join(qinfo_dir, stocknum, 'QINFO')
        print(os.path.isdir(filesetid_qinfo_dir), len(gb.glob(tmp_location + '/*sync*adj*.txt')))
        if (len(gb.glob(tmp_location + '/*sync*adj*.txt')) != 260):
            s3_dir = str(row['bibleid']).strip()
            #s3_dir ="PORBAR"

            create_dirs([os.path.join(corescripts_dir, filesetid)])

            # sh.copy(gb.glob('/Users/spanta/Documents/batch_aeneas_scripts/batch_core_scripts/' + script)[0],
            #         os.path.join(corescripts_dir, filesetid))

            # aws_execstring = 'aws s3 sync s3://dbp-prod/audio/' + s3_dir + '/' + filesetid + '/' + ' ' + os.path.join(
            #     audio_dir,
            #     filesetid) + '/' + ' --exclude "*" --include "*B01*01*.mp3"'

            # aws_execstring = 'aws s3 ls s3://dbp-prod/audio/' + s3_dir + '/' + filesetid + '/'
            # print(aws_execstring)
            # os.system(aws_execstring)
            os.environ["AWS_PROFILE"]="dbs"
            os.environ["AWS_DEFAULT_REGION"]="us-west-2"
            aws_execstring = 'aws s3 --profile dbs sync s3://dbp-prod/audio/' + s3_dir + '/' + filesetid + '/' + ' ' + os.path.join(
                audio_dir,
                filesetid) + '/' + ' --exclude "*" --include "*.mp3"'
            print(aws_execstring)
            os.system(aws_execstring)

            if len(gb.glob(os.path.join(audio_dir,filesetid) + '/*.mp3')) >=260:
                input_audio_dir = os.path.join(audio_dir, filesetid)
                corescripts_location = os.path.join(corescripts_dir, filesetid, script)

                # extract_lines_from_corescript_execstring = 'python3 ' + scripts_dir + '/batch_create_lines_from_corescript_xls.py ' + \
                #                                            ' -core_script ' + corescripts_location + \
                #                                            ' -o ' + tmp_location + ' -book_chapter ' + '\'MAT 1\''
                extract_lines_from_corescript_execstring = 'python3 ' + scripts_dir + '/'+filesetid+'/batch_create_lines_from_corescript_xls.py ' + \
                                                           ' -core_script ' + corescripts_location + ' -input_audio_dir ' + input_audio_dir + \
                                                           ' -input_book_to_audiobookid_mapfile ' + book_to_audioid+ \
                                                           ' -o ' + tmp_location +' -fileset '+filesetid
                print(extract_lines_from_corescript_execstring)
                os.system(extract_lines_from_corescript_execstring)

                lines_csv_location = os.path.join(tmp_location, 'lines.csv')


                # extract_aeneas_execstring = 'python3 ' + scripts_dir + '/batch_new_create_aeneas.py ' \
                #                                                        ' -input_lines_csv ' + lines_csv_location + \
                #                             ' -input_audio_dir ' + input_audio_dir + \
                #                             ' -output_dir ' + tmp_location + \
                #                             ' -book_chapter ' + '\'MAT 1\''\
                #                             ' -language_code epo ' \
                #                             ' -input_book_to_audiobookid_mapfile ' + book_to_audioid
                extract_aeneas_execstring = 'python3 ' + scripts_dir + '/'+filesetid+ '/batch_new_create_aeneas.py ' \
                                                                       ' -input_lines_csv ' + lines_csv_location + \
                                            ' -input_audio_dir ' + input_audio_dir + \
                                            ' -output_dir ' + tmp_location + \
                                            ' -voice_code esperanto -tts_wrapper espeak ' \
                                            ' -input_book_to_audiobookid_mapfile ' + book_to_audioid
                print(extract_aeneas_execstring)
                os.system(extract_aeneas_execstring)

                if len(gb.glob(tmp_location + '/*sync*adj*.txt')) == 260:

                    create_dirs([os.path.join(aeneas_timings_dir, filesetid)])

                    filesetid_timings_dir = aeneas_timings_dir + '/' + filesetid

                    sab_line_timings_dir = filesetid_timings_dir + '/line_timings/'
                    sab_verse_timings_dir = filesetid_timings_dir + '/verse_timings/'

                    create_sab_string = 'python3 ' + scripts_dir + '/'+filesetid+ '/batch_create_sab_files_noQC_nochaphead_read_from_audmarkfile.py ' \
                                                                   ' -i ' + tmp_location + \
                                        ' -o ' + sab_verse_timings_dir + \
                                        ' -input_book_to_audiobookid_mapfile ' + book_to_audioid + \
                                        ' -input_audio_dir ' + input_audio_dir

                    print(create_sab_string)

                    os.system(create_sab_string)

                    create_sab_string = 'python3 ' + scripts_dir + '/batch_create_sab_files_noQC.py ' \
                                                                   ' -i ' + tmp_location + \
                                        ' -o ' + sab_line_timings_dir + \
                                        ' -input_book_to_audiobookid_mapfile ' + book_to_audioid + \
                                        ' -input_audio_dir ' + input_audio_dir + ' -extract_line_timing'
                    print(create_sab_string)
                    os.system(create_sab_string)

                    '''
                    python3 /Users/spanta/Desktop/adapted_for_batch/batch_create_sab_files_noQC.py -i /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/tmp/BMQBSMN2DA/epo
                    -o /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/timings/BMQBSMN2DA/epo/line_timings
                    -input_book_to_audiobookid_mapfile /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/mapping_book_to_audiobookid.csv
                    -input_audio_dir /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/audio/BMQBSMN2DA -extract_line_timing
                    '''

                    # create_dirs([os.path.join(qinfo_dir, filesetid)])


                    print(filesetid_qinfo_dir)

                    extract_line_from_clt_string = 'python3 ' + scripts_dir + '/batch_extract_cue_from_clt_file.py ' \
                                                                              ' -i ' + filesetid_qinfo_dir + \
                                                   ' -o ' + tmp_location + \
                                                   ' -input_book_to_audiobookid_mapfile ' + book_to_audioid + \
                                                   ' -input_audio_dir ' + input_audio_dir
                    #print(extract_line_from_clt_string)
                    #os.system(extract_line_from_clt_string)

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
                    #print(qc_string)
                    #os.system(qc_string)

                    '''
                    python3 /Users/spanta/Desktop/adapted_for_batch/batch_QC.py -cue_info_dir /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/tmp/BMQBSMN2DA/eng
                    -sab_timing_dir /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/timings/BMQBSMN2DA/eng/line_timings
                    -aeneas_dir /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/tmp/BMQBSMN2DA/eng
                    -o /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/tmp/BMQBSMN2DA/eng/QC
                    -input_book_to_audiobookid_mapfile /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/mapping_book_to_audiobookid.csv
                    '''
                    if len(gb.glob(filesetid_qc_dir+'/*95%QC_value_flagged.txt')) ==0 and len(gb.glob(filesetid_qc_dir+'/*95%QC_*.txt')) ==1:
                        #create_dirs([verse_timings_dir+'/'+filesetid])
                        copy_string='cp -fr '+sab_verse_timings_dir+ ' '+verse_timings_dir+'/pass_qc/'+filesetid
                        #os.system(copy_string)
                        copy_string = 'cp -fr ' + filesetid_qc_dir + ' ' + verse_timings_dir + '/pass_qc/' + filesetid
                        #os.system(copy_string)

                    else:
                        with open(scripts_dir + '/languages_QC.txt', 'a') as f:
                            f.write(str(row))
                        f.close()
                        copy_string='cp -fr '+sab_verse_timings_dir+ ' '+verse_timings_dir+'/failed_qc/'+filesetid
                        #os.system(copy_string)
                        copy_string = 'cp -fr ' + filesetid_qc_dir + ' ' + verse_timings_dir + '/failed_qc/' + filesetid
                        #os.system(copy_string)

                    #os.system('rm -fr {}'.format(os.path.join(audio_dir, filesetid)))
                    with open(filesetid_qc_dir+'/runtime.txt','w') as f:
                        f.write(str(time.time() - start_time))
                    f.close()
                    # os.rmdir(os.path.join(audio_dir, filesetid))

                else:
                    with open(scripts_dir + '/languages_other_issues.txt', 'a') as f:
                        f.write(str(row))
                    f.close()
                    copy_string = 'cp -fr ' + scripts_dir + '/languages_other_issues.txt'+' '+ verse_timings_dir + '/other/languages_other_issues.txt'
                    os.system(copy_string)
                    os.system('rm -fr {}'.format(os.path.join(audio_dir, filesetid)))


            else:
                with open(scripts_dir + '/languages_aws_issues.txt', 'a') as f:
                    f.write(str(row))
                f.close()
                copy_string = 'cp -fr ' + scripts_dir + '/languages_aws_issues.txt'+' '+ verse_timings_dir + '/other/languages_aws_issues.txt'
                os.system(copy_string)
                os.system('rm -fr {}'.format(os.path.join(audio_dir, filesetid)))
            os.system('rm -fr {}'.format(os.path.join(audio_dir, filesetid)))


        elif (len(gb.glob(tmp_location + '/*sync*adj*.txt')) == 260) and len(gb.glob(tmp_location+'/QC/*out*val*.txt'))==0:
            #s3_dir = str(row['bibleid']).strip()
            s3_dir ="PORBAR"
            aws_execstring = 'aws s3 sync s3://dbp-prod/audio/' + s3_dir + '/' + filesetid + '/' + ' ' + os.path.join(
                audio_dir,
                filesetid) + '/' + ' --exclude "*" --include "*.mp3"'
            print(aws_execstring)
            os.system(aws_execstring)

            create_dirs([os.path.join(aeneas_timings_dir, filesetid)])
            input_audio_dir = os.path.join(audio_dir, filesetid)
            filesetid_timings_dir = aeneas_timings_dir + '/' + filesetid

            sab_line_timings_dir = filesetid_timings_dir + '/line_timings/'
            sab_verse_timings_dir = filesetid_timings_dir + '/verse_timings/'

            # # Fix rows where verses are recorded as {3,4} and its read as separate fields # Temperary fix to avoid re aeneasing audio
            # from pandas import DataFrame
            # a = []
            # output_file=os.path.join(tmp_location, 'aeneas.csv')
            # qc_filename_read = open(output_file).readlines()
            # for i, line in enumerate(qc_filename_read):
            #     if len(line.split(',')) != 7:
            #         print(line)
            #         l = len(line.split(','))
            #         print(l)
            #         print(3 + (l - 7) + 1)
            #         line = line.split(',')[0] + ',' + line.split(',')[1] + ',' + line.split(',')[2] + ',' + ',' + \
            #                line.split(',')[3] + ',' + str(
            #             line.split(',')[3:3 + (l - 7) + 1]).replace(',', '|') + line.split(',')[-2] + ',' + \
            #                line.split(',')[-1]
            #     a.append(line)
            # adf = DataFrame(a)
            # adf.to_csv(output_file, header=False, index=False)

            create_sab_string = 'python3 ' + scripts_dir + '/batch_create_sab_files_noQC.py ' \
                                                           ' -i ' + tmp_location + \
                                ' -o ' + sab_verse_timings_dir + \
                                ' -input_book_to_audiobookid_mapfile ' + book_to_audioid + \
                                ' -input_audio_dir ' + input_audio_dir

            print(create_sab_string)

            os.system(create_sab_string)

            create_sab_string = 'python3 ' + scripts_dir + '/batch_create_sab_files_noQC.py ' \
                                                           ' -i ' + tmp_location + \
                                ' -o ' + sab_line_timings_dir + \
                                ' -input_book_to_audiobookid_mapfile ' + book_to_audioid + \
                                ' -input_audio_dir ' + input_audio_dir + ' -extract_line_timing'
            print(create_sab_string)
            os.system(create_sab_string)

            '''
            python3 /Users/spanta/Desktop/adapted_for_batch/batch_create_sab_files_noQC.py -i /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/tmp/BMQBSMN2DA/epo
            -o /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/timings/BMQBSMN2DA/epo/line_timings
            -input_book_to_audiobookid_mapfile /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/mapping_book_to_audiobookid.csv
            -input_audio_dir /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/audio/BMQBSMN2DA -extract_line_timing
            '''

            # create_dirs([os.path.join(qinfo_dir, filesetid)])

            print(filesetid_qinfo_dir)

            extract_line_from_clt_string = 'python3 ' + scripts_dir + '/batch_extract_cue_from_clt_file.py ' \
                                                                      ' -i ' + filesetid_qinfo_dir + \
                                           ' -o ' + tmp_location + \
                                           ' -input_book_to_audiobookid_mapfile ' + book_to_audioid + \
                                           ' -input_audio_dir ' + input_audio_dir
            #print(extract_line_from_clt_string)
            # os.system(extract_line_from_clt_string)

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
            #print(qc_string)
            # os.system(qc_string)

            '''
            python3 /Users/spanta/Desktop/adapted_for_batch/batch_QC.py -cue_info_dir /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/tmp/BMQBSMN2DA/eng
            -sab_timing_dir /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/timings/BMQBSMN2DA/eng/line_timings
            -aeneas_dir /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/tmp/BMQBSMN2DA/eng
            -o /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/tmp/BMQBSMN2DA/eng/QC
            -input_book_to_audiobookid_mapfile /Users/spanta/Documents/batch_aeneas_scripts/batch_directory/mapping_book_to_audiobookid.csv
            '''
            if len(gb.glob(filesetid_qc_dir + '/*95%QC_value_flagged.txt')) == 0 and len(
                    gb.glob(filesetid_qc_dir + '/*95%QC_*.txt')) == 1:
                # create_dirs([verse_timings_dir+'/'+filesetid])
                copy_string = 'cp -fr ' + sab_verse_timings_dir + ' ' + verse_timings_dir + '/pass_qc/' + filesetid
                # os.system(copy_string)
                copy_string = 'cp -fr ' + filesetid_qc_dir + ' ' + verse_timings_dir + '/pass_qc/' + filesetid
                # os.system(copy_string)

            else:
                with open(scripts_dir + '/languages_QC.txt', 'a') as f:
                    f.write(str(row))
                f.close()
                copy_string = 'cp -fr ' + sab_verse_timings_dir + ' ' + verse_timings_dir + '/failed_qc/' + filesetid
                os.system(copy_string)
                copy_string = 'cp -fr ' + filesetid_qc_dir + ' ' + verse_timings_dir + '/failed_qc/' + filesetid
                os.system(copy_string)

            # os.system('rm -fr {}'.format(os.path.join(audio_dir, filesetid)))
            with open(filesetid_qc_dir + '/runtime.txt', 'w') as f:
                f.write(str(time.time() - start_time))
            f.close()
            os.rmdir(os.path.join(audio_dir, filesetid))

        else:
            with open(scripts_dir + '/languages_other_issues.txt', 'a') as f:
                f.write(str(row))
            f.close()
            copy_string = 'cp -fr ' + scripts_dir + '/languages_other_issues.txt' + ' ' + verse_timings_dir + '/other/languages_other_issues.txt'
            os.system(copy_string)
            os.system('rm -fr {}'.format(os.path.join(audio_dir, filesetid)))




        # categorize based on this , pass qc, failed qc, other issues
        # s3://dbp-aeneas-staging/verse_timings/passqc/filesetid/sab_timing_files_all_chaps
        # s3://dbp-aeneas-staging/verse_timings/passqc/filesetid/QC/out95 , runtime, qc data
    # aws_execstring = 'aws s3 sync '+  verse_timings_dir+' s3://dbp-aeneas-staging/'
    # print(aws_execstring)
    # os.system(aws_execstring)

run_aeneas()
'''
def main():
    try:
        aeneas()
    except(BrokenPipeError,IOError):
        pass

if __name__ == '__main__':
    main()
'''
