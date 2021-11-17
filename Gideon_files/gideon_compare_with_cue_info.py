import pandas as pd,argparse,glob,statistics as stat,matplotlib.pyplot as plt,numpy as np,operator,re

#Make sure for chinanteco line comparison the cue info first liine is taken care of

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
# required_args.add_argument(
#     '-sab_find_string', required=True, nargs=1, type=str, help='EX: MRK to get MRK1,ESV_MRK_01 etc.')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-strict_comparison', type=int,choices=[1,2], help='1-Compare aeneas and qinfo start boundaries. 2- Compare verse duration and 1')
optional_args.add_argument('-extract_verse_timing', action='store_true', help='Compare verse timing info.')
optional_args.add_argument('-synced_silence', action='store_true', help='Indicate whether the output from aeneas timing was fully synced with silence adjustment')
optional_args.add_argument('-synced_qinfo', action='store_true', help='Indicate whether the output from aeneas timing was fully synced with qinfo')
optional_args.add_argument('-print_chapter', nargs=1, type=str,default=['9'],help='Print chapter')
optional_args.add_argument('-write_audition_format', action='store_true', help='Write output to audition tab csv format')
optional_args.add_argument('-check_secs', nargs=1, type=str,default=['3'],help='Mark if above check secs')

args = parser.parse_args()
input_dir=args.i[0]
output_dir=args.o[0]
book_find_string=args.book_find_string[0]

#sab_find_string=args.sab_find_string[0]

if args.strict_comparison is not None: strict_comparison=args.strict_comparison
else:strict_comparison=0
print_chapter=args.print_chapter[0]


print(args)

input_file='aeneas.csv'
df=(pd.read_csv(input_dir+'/'+input_file, encoding='utf-8')).astype(str)







#change#chapter_list=df['chapter'].unique()


if args.extract_verse_timing: target='verse_number'
else:target='line_number'

if args.synced_silence: aeneas_adjusted_file='*_sync_adjusted.txt'
elif args.synced_qinfo:aeneas_adjusted_file='*_qinfo_adjusted.txt'
else:aeneas_adjusted_file='*_adjusted.txt'



'''
#change
#get column indexes
target_index=df.columns.get_loc(target)


qc_data=dict()
median_dict=dict()
std_dev_dict=dict()

'''









for each_chapter in chapter_list:
    target_list=df[target][df['chapter'] == str(each_chapter)]
    uniq_target=(target_list.unique())[1:]

    if float(each_chapter)<10:
        #Get cue info file
        # change # cue_info_chapter_file=glob.glob(input_dir+'/*'+sab_find_string+'*'+'0'+str(each_chapter)+'*timing.txt')[0]

        #Get aeneas silence adjusted file
        aeneas_chapter_file=glob.glob(input_dir+'/*'+'0'+str(each_chapter)+'_'+book_find_string+'*'+aeneas_adjusted_file)[0]
    else:
        #Get cue info file
        # change #cue_info_chapter_file=glob.glob(input_dir+'/*'+sab_find_string+'*'+str(each_chapter)+'*timing.txt')[0]

        #Get aeneas silence adjusted file
        aeneas_chapter_file = glob.glob(input_dir + '/*' + str(each_chapter) + '_' + book_find_string + '*' + aeneas_adjusted_file)[0]

    if args.write_audition_format:
        audition_file_name = (aeneas_chapter_file.split('/')[-1]).split('_sync_adjusted.txt')[0] + target.split('_')[0]+'_audition_markers.csv'
        #print(aeneas_chapter_file.split('/')[-1],(aeneas_chapter_file.split('/')[-1]).split('_sync_adjusted.txt')[0],audition_file_name)
        audition_file = input_dir + '/' + audition_file_name


        file_name=(aeneas_chapter_file.split('/')[-1]).split('_sync_adjusted.txt')[0]
        chapter=(re.split('\_+', file_name))[1]
        #print(chapter)
        sab_df=pd.read_csv('/Users/spanta/Documents/FCBH_github/GIDEON/final_chapter_lengths_n2_working_copy.csv')
        book_id=(sab_df[(sab_df.iloc[:, 0].str).contains(file_name) == True].iloc[0,1])
        id = str(re.compile('\_+').split(file_name)[0])[1:]
        SAB_timing_filename = input_dir + '/' +'-'.join(['C01', id, 'check', chapter, 'timing.txt'])

    #Read cue info and aeneas for iteration in the foll. for loop
    aeneas_target = open(aeneas_chapter_file).readlines()

    # change #cue_target=open(cue_info_chapter_file).readlines()

    ind=0
    difference_list=list()


    with open(audition_file,'w') as aud:
        with open(SAB_timing_filename,'w') as sab:
            # Since we cant read cue info last verse, we will remove the last element from uniq_target
            # uniq_target=uniq_target[:-1]
            for each_target in uniq_target:
                ind+=1

                #
                if ind<=len(open(cue_info_chapter_file).readlines(  )):

                    '''# change #
                    cue_times=((cue_target[ind-1]).strip('\n')).split('\t')
                    cue_duration=float(cue_times[1])-float(cue_times[0])

                    cue_start=float(cue_times[0])
                    '''

                    indices=[i for i,val in enumerate(target_list) if val==each_target]
                    aeneas_duration = 0

                    counter=0
                    aud_duration=0
                    aud_text=''
                    #print(each_target,indices)
                    for each_index in indices:
                        #print(each_index,aeneas_target[each_index])
                        aeneas_times = ((aeneas_target[each_index]).strip('\n')).split('\t')
                        aeneas_duration += float(aeneas_times[1]) - float(aeneas_times[0])
                        aud_duration=aeneas_duration
                        aud_text+=aeneas_times[-1][1:]

                        if counter==0:
                            aeneas_start=float(((aeneas_target[each_index]).strip('\n')).split('\t')[0])
                            aud_start=aeneas_start
                        counter+=1
                        # print(aeneas_times,aeneas_duration,cue_duration)
                        # print(each_chapter,each_target, each_index,cue_times, aeneas_times)

                    #if int(each_chapter) == 16:print(cue_duration,aeneas_duration)

                    '''# change #
                    difference = (round(abs(cue_duration - aeneas_duration), 1))
                    if difference>12:
                        print(each_chapter,each_target)
                    '''

                    #print(difference)
                    # if each_chapter==print_chapter:
                    #print('AUD->', each_chapter, each_target, each_index, aud_start, aud_duration, aeneas_times[2],aud_text)

                    '''# change #
                    if strict_comparison==1: difference=(round(abs(cue_start - aeneas_start), 1))
                    elif strict_comparison==2:difference=(round(abs(cue_start - aeneas_start), 1))+(round(abs(cue_duration - aeneas_duration), 1))
                    # print(difference)
                    difference_list.append(difference)
                    '''

                    # if each_chapter==print_chapter: print(cue_start,aeneas_start)

                    if difference > float(args.check_secs[0]):
                        marker_name = 'Check_A_Marker_'
                    else:
                        marker_name = 'A_Marker_'

                    if ind==1:
                        # Write to adobe audition file
                        aud.write(
                            'Name' + '\t' + 'Start' + '\t' + 'Duration' + '\t' + 'Time Format' + '\t' + 'Type' + '\t' + 'Description' + '\n')
                        aud.write(marker_name + str(each_target) + '\t' + '0:' + str(round(aud_start, 3)) + '\t' + '0:' + str(
                            round(aud_duration, 3)) + '\t' + 'decimal' + '\t' + 'Cue' + '\t' +aud_text+'\n')

                        # print('aud text->',aud_text)
                    else:
                        aud.write(marker_name + str(each_target) + '\t' + '0:' + str(round(aud_start, 3)) + '\t' + '0:' + str(
                            round(aud_duration, 3)) + '\t' + 'decimal' + '\t' + 'Cue' + '\t' +aud_text+'\n')
                        # print('aud text->', aud_text)

                    sab.write(str(round(aud_start, 2)) + '\t' + str(     round(round(aud_start, 2) + round(aud_duration, 2),2)       ) + '\t' + str(each_target)+'\n')

            # if each_chapter == print_chapter:
            #     print('chapter->',each_chapter)
                #for g, val in enumerate(difference_list):
                    #print(g, val)


            '''# change 
            qc_data[each_chapter]=difference_list
            median_dict[each_chapter]=np.median(difference_list)
            std_dev_dict[each_chapter]=np.std(difference_list)
            '''

'''
    target1='verse_number'
    target1_list = df[target1][df['chapter'] == str(each_chapter)]
    uniq1_target = target1_list.unique()
    if args.write_audition_format:
        audition_file_name = (aeneas_chapter_file.split('/')[-1]).split('_sync_adjusted.txt')[0] + target1.split('_')[0]+'_audition_markers.csv'
        #print(aeneas_chapter_file.split('/')[-1],(aeneas_chapter_file.split('/')[-1]).split('_sync_adjusted.txt')[0],audition_file_name)
        audition_file = input_dir + '/' + audition_file_name

    #Read cue info and aeneas for iteration in the foll. for loop
    aeneas_target = open(aeneas_chapter_file).readlines()
    ind=0

    with open(audition_file,'w') as aud:
        # Since we cant read cue info last verse, we will remove the last element from uniq_target
        # uniq_target=uniq_target[:-1]
        for each_target in uniq1_target:
            ind+=1

            indices=[i for i,val in enumerate(target1_list) if val==each_target]
            aeneas_duration = 0

            counter=0
            aud_duration=0
            aud_text=''
            for each_index in indices:
                aeneas_times = ((aeneas_target[each_index]).strip('\n')).split('\t')
                aeneas_duration += float(aeneas_times[1]) - float(aeneas_times[0])
                aud_duration=aeneas_duration
                aud_text+=aeneas_times[-1][1:]

                if counter==0:
                    aeneas_start=float(((aeneas_target[each_index]).strip('\n')).split('\t')[0])
                    aud_start=aeneas_start
                counter+=1

            marker_name = 'A_Marker_'

            if ind==1:
                # Write to adobe audition file
                print(marker_name + str(each_target) + '\t' + '0:' + str(round(aud_start, 3)) + '\t' + '0:' + str(
                    round(aud_duration, 3)) + '\t' + 'decimal' + '\t' + 'Cue' + '\t' +aud_text+'\n')
                aud.write(
                    'Name' + '\t' + 'Start' + '\t' + 'Duration' + '\t' + 'Time Format' + '\t' + 'Type' + '\t' + 'Description' + '\n')
                aud.write(marker_name + str(each_target) + '\t' + '0:' + str(round(aud_start, 3)) + '\t' + '0:' + str(
                    round(aud_duration, 3)) + '\t' + 'decimal' + '\t' + 'Cue' + '\t' +aud_text+'\n')
                # print('aud text->',aud_text)
            else:
                print(marker_name + str(each_target) + '\t' + '0:' + str(round(aud_start, 3)) + '\t' + '0:' + str(
                    round(aud_duration, 3)) + '\t' + 'decimal' + '\t' + 'Cue' + '\t' +aud_text+'\n')
                aud.write(marker_name + str(each_target) + '\t' + '0:' + str(round(aud_start, 3)) + '\t' + '0:' + str(
                    round(aud_duration, 3)) + '\t' + 'decimal' + '\t' + 'Cue' + '\t' +aud_text+'\n')
                # print('aud text->', aud_text)
'''


'''change 

sorted_median = sorted(median_dict, key=median_dict.get, reverse=True)



n=len(chapter_list)/4
i=0
for c in range(1,len(chapter_list)+1):
    i+=1
    plt.subplot(n,n,c)
    g=sorted_median[i-1]
    plt.text(0.5, 0.5, 'chap '+str(g)+' ,med=' + str(round(median_dict[g],2)) + ' ,std=' + str(round(std_dev_dict[g],2)),
             fontsize=10, ha='left')
    plt.hist(qc_data[g])
#plt.show()


'''