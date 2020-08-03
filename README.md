# verse-timing
Tools to determine the start time of verses in chapter audio files. Please install the required modules for the code to work. Download the requirements.txt file from this repo and do : pip install -r requirements.txt
IDE Used: PyCharm Community Edition 2018.3 (Free) 

Tested to work with exact command line arguments, input files naming convention on Mark gospel for Chinanteco and having line cue info markers text files as shown below. 

The foll. cue info files are manually extracted from clt tool and written in text format. The compare_with_cue_info_chinanteco.py code wont run if it can't find these files in the output dir. Please unzip "Chinanteco_cue_info_text_files.zip" uploaded to github as below.  
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

Place the cue info. files in the output directory. Ex: /Users/spanta/Documents/FCBH_github/outputs


Input files:
ls /Users/spanta/Desktop/jon_code_test/new_files/drive-download-20200107T220609Z-001/Chinanteco_San_Juan_Lealao_N2CLETBL
CORE_Scr_1059r_NT_1ENG__25_Rdr__Chinanteco_de_San_Juan_Lealao_N1_CLE_TBL.xls	N2_CLE_TBL_0037_MRC_09.wav
N2_CLE_TBL_0029_MRC_01.wav							N2_CLE_TBL_0038_MRC_10.wav
N2_CLE_TBL_0030_MRC_02.wav							N2_CLE_TBL_0039_MRC_11.wav
N2_CLE_TBL_0031_MRC_03.wav							N2_CLE_TBL_0040_MRC_12.wav
N2_CLE_TBL_0032_MRC_04.wav							N2_CLE_TBL_0041_MRC_13.wav
N2_CLE_TBL_0033_MRC_05.wav							N2_CLE_TBL_0042_MRC_14.wav
N2_CLE_TBL_0034_MRC_06.wav							N2_CLE_TBL_0043_MRC_15.wav
N2_CLE_TBL_0035_MRC_07.wav							N2_CLE_TBL_0044_MRC_16.wav
N2_CLE_TBL_0036_MRC_08.wav

Example code to run Chinanteco. 

python3.7 /Users/spanta/Documents/FCBH_github/create_lines_from_corescript_xls.py -i /Users/spanta/Documents/FCBH_github/Chinanteco_inputs/CORE_Scr_1059r_NT_1ENG__25_Rdr__Chinanteco_de_San_Juan_Lealao_N1_CLE_TBL.xls -o /Users/spanta/Documents/FCBH_github/outputs/lines.csv -book Mark


Info. about input arguments
parser = argparse.ArgumentParser(
        description='This function creates lines.csv file from core script .xls file')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input core script .xls file')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output file name')
required_args.add_argument('-fileset', nargs=1, type=str,default=['test'],help='custom fileset id')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-sheetname', nargs=1, default=[0],type=int,help='sheetname or # in corescript')
optional_args.add_argument('-book', nargs=1, type=str,help='custom book.EX: Mark')
optional_args.add_argument('-book_chapter', nargs=1, type=str, default=['MATTHEW 1'],help='custom book chapter. Be sure to include the space. EX: John 9')
optional_args.add_argument('-noheader', action='store_true', help='Remove header: fileset,book,chapter,db,sId,sBegin,sEnd')
optional_args.add_argument('-find_string', nargs=1, type=str,default=['MATTHEW CHP 1'],help='string to find input langauge column index in corescript. Default:MATTHEW CHP 1')
optional_args.add_argument('-target_pointer', nargs=1, type=str,default=['2'],help='Integer to add to input language column index to get target language in corescript. '
                                                                                 'Default: find_string column index + 2')
optional_args.add_argument('-line_pointer', nargs=1, type=str,default=['-2'],help='Integer to add to input language column index to get line number in corescript. '
                                                                                'Default: find_string column index - 2')

------------------------


python3 /Users/spanta/Documents/FCBH_github/create_aeneas.py -input_lines_csv /Users/spanta/Documents/FCBH_github/outputs/lines.csv -input_audio_dir /Users/spanta/Documents/FCBH_github/Chinanteco_inputs -output_dir /Users/spanta/Documents/FCBH_github/outputs -language_code epo -sound_find_string MRC -move_adjustment -write_audition_format


Info. about input arguments

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

------------

python3 /Users/spanta/Documents/FCBH_github/compare_with_cue_info_chinanteco.py -i /Users/spanta/Documents/FCBH_github/outputs -o /Users/spanta/Documents/FCBH_github/outputs -book_find_string MRC -synced_silence -write_audition_format -print_chapter 3 -extract_verse_timing

Info. about input arguments

parser = argparse.ArgumentParser(
        description='This function gives quality control metric between cue info and aeneas. Assumes only one book in aeneas.csv, assumes that each line in core script is translated'
                    'to cue info and aeneas, otherwise script fails')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input dir that contains aeneas.csv *aeneas*.txt/*adjusted.txt and *cue_info*.txt')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output dir')
required_args.add_argument(
    '-book_find_string', required=True, nargs=1, type=str, help='EX: MRK to get MRK1,ESV_MRK_01 etc.')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-strict_comparison', type=int,choices=[1,2], help='1-Compare aeneas and qinfo start boundaries. 2- Compare verse duration and 1')
optional_args.add_argument('-extract_verse_timing', action='store_true', help='Compare verse timing info.')
optional_args.add_argument('-synced_silence', action='store_true', help='Indicate whether the output from aeneas timing was fully synced with silence adjustment')
optional_args.add_argument('-synced_qinfo', action='store_true', help='Indicate whether the output from aeneas timing was fully synced with qinfo')
optional_args.add_argument('-print_chapter', nargs=1, type=str,default=['9'],help='Print chapter')
optional_args.add_argument('-write_audition_format', action='store_true', help='Write output to audition tab csv format')
optional_args.add_argument('-check_secs', nargs=1, type=str,default=['3'],help='Mark if above check secs')

