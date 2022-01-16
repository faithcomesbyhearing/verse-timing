

import argparse,glob,os
import pandas as pd
import math

parser = argparse.ArgumentParser(
        description='This function reads get_core_script_stock_number_N2.csv file splits them and runs parallel processing based on number of cpus')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument(
    '-input', required=True, nargs=1, type=str, help='Input file that lists languages')
optional_args.add_argument(
    '-num_cpu', required=True, nargs=1, type=str, help='Number of CPUs to use')

args = parser.parse_args()
input_file=args.input[0]

if args.num_cpu[0] is not None:
    num_cpus=int(args.num_cpu[0])
else:
    num_cpus=os.cpu_count()

scripts_dir='/home/ubuntu/aeneas_test/aeneas_scripts/'

#csv file name to be read in
in_csv = scripts_dir+'/'+input_file



#get the number of lines of the csv file to be read
number_lines = int(sum(1 for row in (open(in_csv))))


#size of rows of data to write to the csv,
#you can change the row size according to your need

rowsize = int(number_lines/num_cpus)
print(rowsize)
def to_csv_batch(src_csv, dst_dir, size=rowsize, index=False):


    # Read source csv
    df = pd.read_csv(src_csv)
    print('running')

    # Initial values
    low = 0
    high = size
    print('run1')

    # Loop through batches
    for i in range(math.ceil(len(df) / size)):

        fname = dst_dir + '/Batch_' + str(i + 1) + '.csv'
        df[low:high].to_csv(fname, index=index)
        print('run2')

        # Update selection
        low = high
        if (high + size < len(df)):
            high = high + size
        else:
            high = len(df)
        print('running1')


to_csv_batch(scripts_dir+'/'+input_file, scripts_dir)
print('running before')
i=0
for each_file in glob.glob(scripts_dir+'/Batch*'):
    input_file=each_file.split('/')[-1]
    i+=1
    print('running last')
    os.system('nohup python3 test_batch_scripts_aws_multiprocess_N1.py -input_file '+input_file+' > ./mylog'+str(i)+'.log  2>&1 &')



