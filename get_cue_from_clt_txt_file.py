import argparse,re,glob

parser = argparse.ArgumentParser(
        description='This function creates cue.txt file from clt file')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input dir containing clt files')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output dir')




args = parser.parse_args()
input_dir=args.i[0]
output_dir=args.o[0]

for input_file in glob.glob(input_dir+'/*.txt'):
    # Open read and write files
    print(input_file)
    read_file=open(input_file,'r')
    filename = (input_file.split('/')[-1]).split('.')[0]
    write_file=open(output_dir+'/'+filename+'_cue_info.txt','w')

    # Adjust decoding patterm in .clt
    check_list=list()
    for i,lines in enumerate(read_file.readlines()):


        cue1=lines.split('\t')[0]
        cue2=lines.split('\t')[1]
        info='_'.join((lines.split('\t')[2]).split(' '))

        check_list.append(cue2)



        if i==0:
            write_file.write('0.000'+'\t'+str(cue1)+'\t'+'Chapter_heading'+'\n')
            write_file.write(str(cue1) + '\t' + str(cue2) + '\t' + str(info))
        elif float(cue2)>float(check_list[i-1]):
            write_file.write(str(cue1) + '\t' + str(cue2) + '\t' + str(info))
        # if i==10:
        #     write_file.write(str(cue1) + '\t' + str(cue2) + '\t' + str(info))
        #     print(cue2, check_list[i - 1])
        #     print(str(cue1) + '\t' + str(cue2) + '\t' + str(info))

    read_file.close()
    write_file.close()


    # bits_per_second=float((lines[2]).strip())
    #
    # start_time_id=3
    # line_number_id=5
    # increment=5
    # '''IMPL the cues in core script are recorded in the clt as cue 01 for mat 24
    # In core script it says +2 secs, its duration in clt is 1.66 secs'''
    #
    # while line_number_id<=len(lines):
    #
    #     start_time=round(float(lines[start_time_id].strip())/bits_per_second,3)
    #     line_audio_file = (lines[line_number_id]).strip()
    #     line_number=(re.compile('\_+').split(line_audio_file.split('.')[0]))[-1]
    #     write_file.write(str(line_number)+'\t'+str(start_time)+'\n')
    #     start_time_id+=increment
    #     line_number_id+=increment