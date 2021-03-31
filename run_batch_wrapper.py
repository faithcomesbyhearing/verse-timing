
'''
Things to address

filename conventions for mp3

'''


import argparse,re,pandas as pd,os,csv,sys,glob
from num2words import num2words
from langdetect import detect

def dir_path(path):
    if os.path.isdir(path) and os.access(path, os.R_OK):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid directory path")

def out_dir_path(path):
    if os.path.isdir(path) and os.access(path, os.W_OK):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid directory path")

def file_path(path):
    if os.path.isfile(path) and os.access(path, os.R_OK):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid file path")

parser = argparse.ArgumentParser(
        description='This batch wrapper creates the arguments to call aeneas scripts. It expects input dirs to contain data in filesetid named dirs ')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-batch_file', required=True, nargs=1, type=file_path, help='Full path to xlsx/csv core scripts for batch processing')
required_args.add_argument(
    '-batch_files_dir', required=True, nargs=1, type=dir_path, help='Full path to dir for writing batch tmp output files')
required_args.add_argument(
    '-stock_to_fileset_mapping_file', required=True, nargs=1, type=file_path, help='Full path to file for matching stock# to filesetid')
required_args.add_argument(
    '-input_audio_dir', required=True, nargs=1, type=dir_path, help='Full path to dir for input')
required_args.add_argument(
    '-input_core_scripts_dir', required=True, nargs=1, type=dir_path, help='Full path to dir having core scripts')
required_args.add_argument(
    '-input_qinfo_dir', required=True, nargs=1, type=dir_path, help='Full path to dir having qinfo files')
required_args.add_argument(
    '-output_timing_dir', required=True, nargs=1, type=out_dir_path, help='Full path to output dir for writing timing files in SAB format for upload')




args = parser.parse_args()
print(args)
batch_corescripts_file=args.batch_file[0]
stock_to_fileset_mapping_file=args.stock_to_fileset_mapping_file[0]



def load_excel_file(file):
    #Get file extension and load file accordingly
    fn, fe = os.path.splitext(file)

    #Load the file
    if fe=='.XLSX':
        input_df=pd.read_excel(file,encoding='utf-8').astype(str)
        print(input_df['verse_content1'])

    elif fe=='.csv':
        input_df = pd.read_csv(file, encoding='utf-8').astype(str)

    return input_df

batch_df=load_excel_file(batch_corescripts_file)
filesetid_df=load_excel_file(stock_to_fileset_mapping_file)

merged_df = pd.merge(batch_df, filesetid_df, how="inner", on='stocknumber')


for index,row in batch_df.iterrows():
    if str(row['stocknumber']).__contains__('2'):
        audio_type = 'audio_drama'
    else:
        audio_type = 'audio'
    corescript_file=row['corescript_file']
    filesetid=((merged_df[    (merged_df['type']==audio_type)  & (merged_df["filesetid_y"].str.contains('16')==0)  & (merged_df["stocknumber"]==row['stocknumber']) ]['filesetid_y']).drop_duplicates()).to_string(index=False).strip()

    print(corescript_file)



