# verse-timing
Tools to determine the start time of verses in chapter audio files.
Example code to run Chinanteco

python3 upload_code/create_lines_from_corescript_xls.py -i new_files/drive-download-20200107T220609Z-001/Chinanteco_San_Juan_Lealao_N2CLETBL/CORE_Scr_1059r_NT_1ENG__25_Rdr__Chinanteco_de_San_Juan_Lealao_N1_CLE_TBL.xls -o /Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/chinanteco_lines.csv -book Mark 


python3 upload_code/create_aeneas.py -input_lines_csv /Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/chinanteco_lines.csv -input_audio_dir /Users/spanta/Desktop/jon_code_test/new_files/drive-download-20200107T220609Z-001/Chinanteco_San_Juan_Lealao_N2CLETBL -output_dir upload_code/chinanteco_aeneas/lang_code_epo -language_code epo -sound_find_string MRC -adjust_silence -write_audition_format


python3 upload_code/compare_with_cue_info_chinanteco.py -i /Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo -o /Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas -book_find_string MRC -synced_silence -write_audition_format -print_chapter 3 -extract_verse_timing



The foll. cue info files are manually extracted from clt tool and written in text format
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.029.MRC.01_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.030.MRC.02_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.031.MRC.03_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.032.MRC.04_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.033.MRC.05_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.034.MRC.06_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.035.MRC.07_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.036.MRC.08_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.037.MRC.09_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.038.MRC.10_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.039.MRC.11_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.040.MRC.12_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.041.MRC.13_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.042.MRC.14_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.043.MRC.15_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.044.MRC.16_cue_info.txt
