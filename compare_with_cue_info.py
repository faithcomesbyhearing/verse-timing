import pandas as pd,argparse,glob,statistics as stat,matplotlib.pyplot as plt,numpy as np,operator

parser = argparse.ArgumentParser(
        description='This function gives quality control metric between cue info and aeneas. Assumes only one book in aeneas.csv, assumes that each line in core script is translated'
                    'to cue info and aeneas, otherwise script fails')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input dir that contains aeneas.csv *aeneas*.aud/*adjusted.aud and *cue_info*.txt')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output dir')
required_args.add_argument(
    '-book_find_string', required=True, nargs=1, type=str, help='EX: MRK to get MRK1,ESV_MRK_01 etc.')

args = parser.parse_args()
input_dir=args.i[0]
output_dir=args.o[0]
book_find_string=args.book_find_string[0]

input_file='aeneas.csv'
df=(pd.read_csv(input_dir+'/'+input_file, encoding='utf-8')).astype(str)

#Get unique book and chapters
book_list=df['book'].unique()
chapter_list=df['chapter'].unique()

#get column indexes
line_number_index=df.columns.get_loc("line_number")


qc_data=dict()
median_dict=dict()
std_dev_dict=dict()
for each_chapter in chapter_list:
    line_list=df['line_number'][df['chapter'] == str(each_chapter)]
    uniq_lines=line_list.unique()

    if float(each_chapter)<10:
        #Get cue info file
        cue_info_chapter_file=glob.glob(input_dir+'/*'+book_find_string+'*'+'0'+str(each_chapter)+'_cue_info.txt')[0]

        #Get aeneas silence adjusted file
        aeneas_chapter_file=glob.glob(input_dir+'/*'+book_find_string+'*'+'0'+str(each_chapter)+'_adjusted.aud')[0]
    else:
        #Get cue info file
        cue_info_chapter_file=glob.glob(input_dir+'/*'+book_find_string+'_'+str(each_chapter)+'_cue_info.txt')[0]

        #Get aeneas silence adjusted file
        aeneas_chapter_file=glob.glob(input_dir+'/*'+book_find_string+'_'+str(each_chapter)+'_adjusted.aud')[0]

    #Read lines of cue info and aeneas for iteration in the foll. for loop
    aeneas_lines = open(aeneas_chapter_file).readlines()
    cue_lines=open(cue_info_chapter_file).readlines()

    ind=0
    difference_list=list()
    for each_line in uniq_lines:
        ind+=1

        if ind<=len(open(cue_info_chapter_file).readlines(  )):
            cue_times=((cue_lines[ind-1]).strip('\n')).split('\t')
            cue_duration=float(cue_times[1])-float(cue_times[0])



            indices=[i for i,val in enumerate(line_list) if val==each_line]
            aeneas_duration = 0
            for each_index in indices:
                aeneas_times = ((aeneas_lines[each_index]).strip('\n')).split('\t')
                aeneas_duration += float(aeneas_times[1]) - float(aeneas_times[0])
                # print(aeneas_times,aeneas_duration,cue_duration)

            #if int(each_chapter) == 16:print(cue_duration,aeneas_duration)
            difference = (round(abs(cue_duration - aeneas_duration), 1))
            # print(difference)
            difference_list.append(difference)
    qc_data[each_chapter]=difference_list
    median_dict[each_chapter]=np.median(difference_list)
    std_dev_dict[each_chapter]=np.std(difference_list)

    # print(difference_list,stat.median(difference_list),stat.stdev(difference_list),len(difference_list))
    # plt.hist(difference_list)
    # fig = plt.figure()
    # fig.canvas.set_window_title('chapter'+each_chapter)
    # plt.show()

sorted_median = sorted(median_dict, key=median_dict.get, reverse=True)
# print(median_dict,sorted_median)


# for i in sorted_median:
#     plt.title('chapter_'+str(i)+' ,median='+str(median_dict[i])+' ,std dev='+str(std_dev_dict[i]))
#     plt.hist(qc_data[i])
#     plt.show()

n=len(chapter_list)/4
i=0
for c in range(1,len(chapter_list)+1):
    i+=1
    plt.subplot(n,n,c)
    g=sorted_median[i-1]
    plt.text(0.5, 0.5, 'chap '+str(g)+' ,med=' + str(round(median_dict[g],2)) + ' ,std=' + str(round(std_dev_dict[g],2)),
             fontsize=10, ha='left')
    plt.hist(qc_data[g])
plt.show()











