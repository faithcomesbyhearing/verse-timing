import pandas as pd,argparse,glob,statistics as stat,matplotlib.pyplot as plt,numpy as np,operator

'''
ex:
python3 upload_code/compare_with_cue_info_chinanteco.py -i /Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo -o /Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas -book_find_string MRC -synced_silence -write_audition_format -print_chapter 3 -extract_verse_timing

'''

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
if args.strict_comparison is not None: strict_comparison=args.strict_comparison
else:strict_comparison=0
print_chapter=args.print_chapter[0]


print(args)

input_file='aeneas.csv'
df=(pd.read_csv(input_dir+'/'+input_file, encoding='utf-8')).astype(str)

#Get unique book and chapters
book_list=df['book'].unique()
chapter_list=df['chapter'].unique()


if args.extract_verse_timing: target='verse_number'
else:target='line_number'

if args.synced_silence: aeneas_adjusted_file='*_sync_adjusted.txt'
elif args.synced_qinfo:aeneas_adjusted_file='*_qinfo_adjusted.txt'
else:aeneas_adjusted_file='*_adjusted.txt'




#get column indexes
target_index=df.columns.get_loc(target)


qc_data=dict()
median_dict=dict()
std_dev_dict=dict()
for each_chapter in chapter_list:
    target_list=df[target][df['chapter'] == str(each_chapter)]
    uniq_target=target_list.unique()

    if float(each_chapter)<10:
        #Get cue info file
        cue_info_chapter_file=glob.glob(input_dir+'/*'+book_find_string+'*'+'0'+str(each_chapter)+'*_cue_info.txt')[0]

        #Get aeneas silence adjusted file
        aeneas_chapter_file=glob.glob(input_dir+'/*'+book_find_string+'*'+'0'+str(each_chapter)+aeneas_adjusted_file)[0]
    else:
        #Get cue info file
        cue_info_chapter_file=glob.glob(input_dir+'/*'+book_find_string+'*'+str(each_chapter)+'*_cue_info.txt')[0]

        #Get aeneas silence adjusted file
        aeneas_chapter_file=glob.glob(input_dir+'/*'+book_find_string+'_'+str(each_chapter)+aeneas_adjusted_file)[0]

    if args.write_audition_format:
        audition_file_name = (aeneas_chapter_file.split('/')[-1]).split('_sync_adjusted.txt')[0] + target.split('_')[0]+'_audition_markers.csv'
        #print(aeneas_chapter_file.split('/')[-1],(aeneas_chapter_file.split('/')[-1]).split('_sync_adjusted.txt')[0],audition_file_name)
        audition_file = input_dir + '/' + audition_file_name

    #Read cue info and aeneas for iteration in the foll. for loop
    aeneas_target = open(aeneas_chapter_file).readlines()
    cue_target=open(cue_info_chapter_file).readlines()

    ind=0
    difference_list=list()


    with open(audition_file,'w') as aud:
        # Since we cant read cue info last verse, we will remove the last element from uniq_target
        # uniq_target=uniq_target[:-1]
        for each_target in uniq_target:
            ind+=1

            #
            if ind<=len(open(cue_info_chapter_file).readlines(  )):
                cue_times=((cue_target[ind-1]).strip('\n')).split('\t')
                cue_duration=float(cue_times[1])-float(cue_times[0])

                cue_start=float(cue_times[0])


                indices=[i for i,val in enumerate(target_list) if val==each_target]
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
                    # print(aeneas_times,aeneas_duration,cue_duration)
                    # print(each_chapter,each_target, each_index,cue_times, aeneas_times)

                #if int(each_chapter) == 16:print(cue_duration,aeneas_duration)
                difference = (round(abs(cue_duration - aeneas_duration), 1))
                #print(difference)
                # if each_chapter==print_chapter:
                #print('AUD->', each_chapter, each_target, each_index, aud_start, aud_duration, aeneas_times[2],aud_text)
                if strict_comparison==1: difference=(round(abs(cue_start - aeneas_start), 1))
                elif strict_comparison==2:difference=(round(abs(cue_start - aeneas_start), 1))+(round(abs(cue_duration - aeneas_duration), 1))
                # print(difference)
                difference_list.append(difference)
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
                #print(marker_name + str(each_target) + '\t' + '0:' + str(round(aud_start, 3)) + '\t' + '0:' + str(round(aud_duration, 3)) + '\t' + 'decimal' + '\t' + 'Cue' + '\t' +aud_text+'\n')
                aud.write(
                    'Name' + '\t' + 'Start' + '\t' + 'Duration' + '\t' + 'Time Format' + '\t' + 'Type' + '\t' + 'Description' + '\n')
                aud.write(marker_name + str(each_target) + '\t' + '0:' + str(round(aud_start, 3)) + '\t' + '0:' + str(
                    round(aud_duration, 3)) + '\t' + 'decimal' + '\t' + 'Cue' + '\t' +aud_text+'\n')
                # print('aud text->',aud_text)
            else:
                #print(marker_name + str(each_target) + '\t' + '0:' + str(round(aud_start, 3)) + '\t' + '0:' + str(round(aud_duration, 3)) + '\t' + 'decimal' + '\t' + 'Cue' + '\t' +aud_text+'\n')
                aud.write(marker_name + str(each_target) + '\t' + '0:' + str(round(aud_start, 3)) + '\t' + '0:' + str(
                    round(aud_duration, 3)) + '\t' + 'decimal' + '\t' + 'Cue' + '\t' +aud_text+'\n')
                # print('aud text->', aud_text)




        qc_data[each_chapter]=difference_list
        median_dict[each_chapter]=np.median(difference_list)
        std_dev_dict[each_chapter]=np.std(difference_list)




    target1='verse_number'
    target1_list = df[target1][df['chapter'] == str(each_chapter)]
    uniq1_target = target1_list.unique()

    target2='line_number'
    target2_list = df[target2][df['chapter'] == str(each_chapter)]
    uniq2_target = target2_list.unique()

    line_cue_target = open(cue_info_chapter_file).readlines()

    # if each_chapter==print_chapter:
    #     print(uniq1_target,uniq2_target)

    if args.write_audition_format:
        audition_file_name = (aeneas_chapter_file.split('/')[-1]).split('_sync_adjusted.txt')[0] + '_'+target1.split('_')[0]+'_curated_audition_markers.csv'
        #print(aeneas_chapter_file.split('/')[-1],(aeneas_chapter_file.split('/')[-1]).split('_sync_adjusted.txt')[0],audition_file_name)
        audition_file = input_dir + '/' + audition_file_name

    silence_file=glob.glob(input_dir+'/'+(aeneas_chapter_file.split('/')[-1]).split('_sync_adjusted.txt')[0]+'*silence*')[0]


    #Read cue info and aeneas for iteration in the foll. for loop
    aeneas_target = open(aeneas_chapter_file).readlines()
    ind=0

    with open(audition_file,'w') as aud:
        # Since we cant read cue info last verse, we will remove the last element from uniq_target
        # uniq_target=uniq_target[:-1]

        for each_target in uniq1_target:
            ind+=1

            indices=[i for i,val in enumerate(target1_list) if val==each_target]


            #Find the next verse index
            for k,kval in enumerate(target1_list):
                if int(kval)==(int(each_target)+1):
                    next_verse_index=k
                    break

                # Find the previous verse index
            for k, kval in enumerate(target1_list):
                if int(kval) == (int(each_target) - 1):
                    previous_verse_index = k
                    break



            # if each_chapter==print_chapter:
            #     print(int(each_target)+1,next_verse_index)

            aeneas_duration = 0

            counter=0
            aud_duration=0
            aud_text=''


            for g,each_index in enumerate(indices):
                aeneas_times = ((aeneas_target[each_index]).strip('\n')).split('\t')
                aeneas_duration += float(aeneas_times[1]) - float(aeneas_times[0])
                aud_duration=aeneas_duration
                aud_text=aud_text+' '+aeneas_times[-1][1:]

                if counter==0:
                    aeneas_start=float(((aeneas_target[each_index]).strip('\n')).split('\t')[0])

                    # aeneas_start_next=float(((aeneas_target[each_index+1]).strip('\n')).split('\t')[0])

                    aud_start=aeneas_start


                    if ind>1 and (float(target2_list.iloc[each_index])-float(target2_list.iloc[each_index-1]))==1 :

                        # if each_chapter==print_chapter:
                        #     print(each_target,target2_list.iloc[each_index])

                        #Get adjustboundary1
                        for i,each_line in enumerate(uniq2_target):
                            if each_line==target2_list.iloc[each_index]:
                                # if each_chapter==print_chapter:
                                #     print("chapter-{0},verse_num-{1},verse index-{2},line_num-{3}".format(each_chapter,each_target,each_index, float(target2_list.iloc[each_index])))

                                adjust_boundary1=float((line_cue_target[i]).split('\t')[0])
                                # if each_chapter==print_chapter:
                                #     print(each_target, each_line,adjust_boundary1)
                                break
                        if each_chapter==print_chapter:
                            aeneas_start_next = float(
                                ((aeneas_target[next_verse_index]).strip('\n')).split('\t')[0])


                        #Read silence file
                        silence_split_field=','
                        with open(silence_file,'r') as s:
                            for silence_bounds in s:
                                silence_start=float(silence_bounds.split(silence_split_field)[0])
                                silence_end=float(silence_bounds.split(silence_split_field)[1])

                                #if boundary falls inside silence, move it to silence region mid point



                                if ind<len(aeneas_target):
                                    aeneas_start_next = float(
                                        ((aeneas_target[next_verse_index]).strip('\n')).split('\t')[0])

                                    aeneas_start_previous=float(
                                        ((aeneas_target[previous_verse_index]).strip('\n')).split('\t')[0])

                                    # if each_chapter==print_chapter and int(each_target)==14:
                                    #     print(each_target, aeneas_start, int(each_target) + 1, aeneas_start_next)


                                    # if each_chapter==print_chapter:
                                    #     print('adjust_boundary1->{0},next_verse_start_time->{1},each_target_verse->{2}'.format(adjust_boundary1,aeneas_start_next,each_target))

                                    if silence_end - silence_start >= 0.45 and silence_start <= adjust_boundary1 <= silence_end and aeneas_start_previous<adjust_boundary1 < aeneas_start_next :
                                        #if each_chapter == print_chapter:
                                            #print("chapter-{0},verse_num-{1},verse index-{2},line_num-{3}".format(
                                                #each_chapter, each_target, each_index,
                                                #float(target2_list.iloc[each_index])))
                                            #print('hey its chapt 3', each_target, adjust_boundary1, aeneas_start_next)
                                        adjust_boundary1 = (silence_start + silence_end) / 2
                                        aud_start = adjust_boundary1
                                        delta = aud_start - adjust_boundary1
                                        # aud_duration=aud_duration-delta
                                        break
                                else:
                                    if silence_end - silence_start >= 0.45 and silence_start <= adjust_boundary1 <= silence_end:
                                        #if each_chapter == print_chapter:
                                            #print("chapter-{0},verse_num-{1},verse index-{2},line_num-{3}".format(
                                                #each_chapter, each_target, each_index,
                                                #float(target2_list.iloc[each_index])))
                                            #print('hey its chapt 3', each_target, adjust_boundary1, aeneas_start_next)
                                        adjust_boundary1 = (silence_start + silence_end) / 2
                                        aud_start = adjust_boundary1
                                        delta = aud_start - adjust_boundary1
                                        # aud_duration=aud_duration-delta
                                        break

                        s.close()

                counter += 1

            marker_name = 'A_Marker_'

            if ind==1:
                # Write to adobe audition file
                aud.write(
                    'Name' + '\t' + 'Start' + '\t' + 'Duration' + '\t' + 'Time Format' + '\t' + 'Type' + '\t' + 'Description' + '\n')
                aud.write(marker_name + str(each_target) + '\t' + '0:' + str(round(aud_start, 3)) + '\t' + '0:' + str(
                    round(aud_duration, 3)) + '\t' + 'decimal' + '\t' + 'Cue' + '\t' +aud_text+'\n')

            else:

                # print(aud_start)
                aud.write(marker_name + str(each_target) + '\t' + '0:' + str(round(aud_start, 3)) + '\t' + '0:' + str(
                    round(aud_duration, 3)) + '\t' + 'decimal' + '\t' + 'Cue' + '\t' +aud_text+'\n')




    #Makers have been adjusted , now adjust durations to match the markers

    #Load audition verse file to update duration
    #print(audition_file)
    aud_df=pd.read_csv(audition_file, encoding='utf-8',sep='\t')


    verses=open(audition_file).readlines()
    conv_string_to_secs = [60, 1]

    for i,each_verse in enumerate(verses):
        if 0<i<len(verses)-1:
            verse_num=(each_verse.split('\t')[0])
            timestr=(each_verse.split('\t')[1])
            current_verse_start_time=sum([a * b for a, b in zip(conv_string_to_secs, map(float, timestr.split(':')))])

            timestr = (each_verse.split('\t')[2])
            current_verse_duration=sum([a * b for a, b in zip(conv_string_to_secs, map(float, timestr.split(':')))])


            current_verse_end_time=current_verse_start_time+current_verse_duration

            #Get next verse begin time
            next_verse=verses[i+1]
            timestr = (next_verse.split('\t')[1])
            next_verse_start_time = sum([a * b for a, b in zip(conv_string_to_secs, map(float, timestr.split(':')))])

            # if each_chapter==print_chapter:
            #     print(each_chapter, verse_num, current_verse_start_time, current_verse_end_time, next_verse_start_time)
            delta = next_verse_start_time - current_verse_end_time

            if each_chapter==print_chapter:
                print(each_verse,current_verse_end_time,next_verse_start_time)


            if next_verse_start_time!=current_verse_end_time:

                if delta>60: print(each_chapter,verse_num,delta,current_verse_start_time,current_verse_end_time,next_verse_start_time,"CHECK delta is >60")
                new_current_verse_duration=current_verse_duration+delta

                new_current_verse_duration=round(new_current_verse_duration,3)


                if new_current_verse_duration<10:
                    new_current_verse_duration='0:0'+str(new_current_verse_duration)
                else:
                    new_current_verse_duration = '0:' + str(new_current_verse_duration)

                aud_df['Duration'][i-1]=new_current_verse_duration

                if float(     (aud_df['Duration'][i]).split(':')[1]          )<0:
                     print(each_chapter,delta,current_verse_duration,aud_df['Duration'][i-1])

                #print(aud_df['Duration'][i])
    #if each_chapter==print_chapter:
        #print(aud_df['Duration'])
    aud_df.to_csv(audition_file,encoding='utf-8',sep='\t',index=False)

















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