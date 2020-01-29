import struct,scipy.io.wavfile as s,argparse,glob,csv,pandas as pd

parser = argparse.ArgumentParser(
        description='This function extracts cue info from wav files')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input dir with wav files')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output dir')
required_args.add_argument(
    '-book_find_string', required=True, nargs=1, type=str, default=['MARK'],help='EX: MRK to get MRK1,ESV_MRK_01 etc.')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-aeneas_find_string', type=str, default=['sync_adjusted'],help='Aeneas names wild card')
optional_args.add_argument('-silence_find_string', type=str, default=['aeneas_out_silence'], help='Silence file names wild card')
optional_args.add_argument('-aeneas_sync_cue_info', action='store_true', help='Sync aeneas output with cue_info')
optional_args.add_argument('-mp3', action='store_true', help='Indicate if its .mp3 or else .wav is taken')
optional_args.add_argument('-is_verses', action='store_true', help='Is verses, as opposed to lines')

args = parser.parse_args()
input_dir=args.i[0]
output_dir=args.o[0]
book_find_string=args.book_find_string[0]


aeneas_dir=output_dir
if args.aeneas_find_string is not None: aeneas_find_string=args.aeneas_find_string[0]
else:aeneas_find_string='sync_adjusted'
if args.silence_find_string is not None: silence_find_string=args.silence_find_string[0]
else:silence_find_string='aeneas_out_silence'

print(args)

audio_type='*.wav'
if args.mp3: audio_type='*.mp3'

if args.is_verses: target='verse_number'
else:target='line_number'

def range1(start, end):
    return range(start, end+1)


def readmarkers(input_dir, mmap=False):
    df = (pd.read_csv(aeneas_dir + '/' + 'aeneas.csv', encoding='utf-8')).astype(str)
    chapter_list = df['chapter'].unique()

    for each_chapter in chapter_list:
        target_list = df[target][df['chapter'] == str(each_chapter)]
        uniq_target = target_list.unique()

        print((input_dir+'/*'+book_find_string+'*'+'0'+str(each_chapter)+audio_type))
        if float(each_chapter)<10:
            #Get audio
            file=glob.glob(input_dir+'/*'+book_find_string+'*'+'0'+str(each_chapter)+audio_type)[0]

        else:
            #Get audio
            file=glob.glob(input_dir+'/*'+book_find_string+'_'+str(each_chapter)+audio_type)[0]

        #Get verse indices from aeneas.csv
        for each_target in uniq_target:
            indices = [i for i, val in enumerate(target_list) if val == each_target]

        # -------------------------Start of cue info extraction------------------------------------------
        file_name=((file.split('/')[-1]).split('.'))[0]
        write_file=open(output_dir+'/'+file_name+'_cue_info.txt', 'w')
        writer = csv.writer(write_file)
        if hasattr(file, 'read'):
            fid = file
        else:
            fid = open(file, 'rb')
        fsize = s._read_riff_chunk(fid)
        cue = []
        while (fid.tell() < fsize[0]):
            chunk_id = fid.read(4)
            if chunk_id == b'cue ':
                size, numcue = struct.unpack('<ii', fid.read(8))
                for c in range(numcue):
                    id, position, datachunkid, chunkstart, blockstart, sampleoffset = struct.unpack('<iiiiii',
                                                                                                    fid.read(24))
                    cue.append(position)
            else:
                s._skip_unknown_chunk(fid, False)
        fid.close()
        cue=[round(x/44100,3) for x in cue]

        corrected_cue=list()
        corrected_cue.append(cue[0])
        # Check values in cue info so that the cues are not misplaced
        for i in range1(1, len(cue) - 1):
            if cue[i] > cue[i - 1]: corrected_cue.append(cue[i])

        # Format the cue info. like aud format
        final_cue = list()
        # print(file,corrected_cue)
        for i, each_cue in enumerate(corrected_cue):

            if args.is_verses:
                if i == 0:

                    final_cue.append('0.000' + '\t' + str(each_cue) + '\t' + str(i))
                    final_cue.append(str(each_cue) + '\t' + str(corrected_cue[i + 1]) + '\t' + str(i + 1))
                elif i > 1:
                    final_cue.append(str(corrected_cue[i - 1]) + '\t' + str(each_cue) + '\t' + str(i))
            else:
                if i == 0:
                    final_cue.append('0.000' + '\t' + str(each_cue))
                else:
                    final_cue.append(str(corrected_cue[i - 1]) + '\t' + str(each_cue))

            if i <= 1: print(final_cue)

        writer.writerows(zip(final_cue))
        write_file.close()
        # print(final_cue)

#-------------------------End of cue info extraction------------------------------------------

        # if args.aeneas_sync_cue_info:
        #     aeneas_file=glob.glob(aeneas_dir+'/'+file_name+'*_'+aeneas_find_string+'.txt')
        #     cue_file=glob.glob(aeneas_dir+'/'+file_name+'*_'+'cue_info'+'.txt')
        #     silence_file=glob.glob(aeneas_dir+'/'+file_name+'*_'+silence_find_string+'.txt')
        #     output_file=aeneas_dir+'/'+file_name+'_'+'cue_info_synced'+'.txt'
        #
        #
        #     # define delimeters
        #     aeneas_split_field = ','
        #     silence_split_field=','
        #     cue_split_field = ','
        #     output_split_field = ','
        #
        #
        #     # Get silence file into a list
        #     silence_dict=dict()
        #     counter=0
        #     with open(silence_file, 'r') as sil:
        #         for line in sil:
        #             line = line.replace('\n', '')
        #             silence_dict[counter]=[float(line.split(silence_split_field)[0]),float(line.split(silence_split_field)[1])]
        #             counter+=1
        #
        #
        #     move_time = 0
        #     inc = 0
        #     with open(aeneas_file, 'r') as f:
        #         with open(output_file, 'w') as up:
        #             # Read input file
        #             for line in f:
        #                 line = line.replace('\n', '')
        #                 adjust_boundary0 = float(line.split(aeneas_split_field)[0])
        #                 adjust_boundary1 = float(line.split(aeneas_split_field)[1]) + move_time
        #                 if len(line.split(input_split_field)) > 2:
        #                     text = output_split_field + line.split(aeneas_split_field)[2]
        #                 else:
        #                     text = ''
        #                 inc += 1
        #
        #                 # Read cue_info file
        #                 with open(cue_file, 'r') as s:
        #                     for cue_info_bounds in s:
        #                         cue_info_start = float(cue_info_bounds.split(cue_split_field)[0])
        #                         cue_info_end = float(cue_info_bounds.split(cue_split_field)[1])
        #
        #                         # if aeneas+- cue_info falls in a silence interval then move aeneas to that silence interval and tag the silence interval as done.
        #                         if cue_info_start <= adjust_boundary1 <= cue_info_end:
        #                             adjust_boundary1 = (cue_info_start + cue_info_end) / 2
        #                             move_time += ((cue_info_start + cue_info_end) / 2) - adjust_boundary1
        #                             break
        #                 s.close()
        #                 new0.append(adjust_boundary1)
        #                 # Write to output file
        #                 if inc == 1:
        #                     up.write(str(round(adjust_boundary0, 3)) + output_split_field + str(
        #                         round(adjust_boundary1, 3)) + text + '\n')
        #                 else:
        #                     up.write(str(round(new0[inc - 2], 3)) + output_split_field + str(
        #                         round(adjust_boundary1, 3)) + text + '\n')
        #         up.close()
        #     f.close()



readmarkers(input_dir)
#
# def aeneas_sync_cue_info(input_file,cue_info_file,output_file,input_split_field=',',cue_info_split_field=',',output_split_field=','):
#     #This function adjusts the boundaries of input file with cue_info mid points
#     inc=0
#     new0=list()
# #     old=list()
# #
# #     with open(input_file, 'r') as f:
# #         for line in f:
# #             line = line.replace('\n', '')
# #             bound0 = float(line.split(input_split_field)[0])
# #             bound1 = float(line.split(input_split_field)[1])
# #             if len(line.split(input_split_field)) > 2: text = output_split_field + line.split(input_split_field)[2]
# #             else:text=''
# #             old.append(['{0} {1} {2}'.format(bound0,bound1,text)])
# #
# # #convert old to int
#
#
#
#     move_time=0
#
#
#     with open(input_file,'r') as f:
#         with open(output_file,'w') as up:
#             #Read input file
#             for line in f:
#                 line=line.replace('\n','')
#                 adjust_boundary0=float(line.split(input_split_field)[0])
#                 adjust_boundary1 = float(line.split(input_split_field)[1])+move_time
#                 if len(line.split(input_split_field))>2: text=output_split_field+line.split(input_split_field)[2]
#                 else:text=''
#                 inc += 1
#
#                 #Read cue_info file
#                 with open(cue_info_file,'r') as s:
#                     for cue_info_bounds in s:
#                         cue_info_start=float(cue_info_bounds.split(cue_info_split_field)[0])
#                         cue_info_end=float(cue_info_bounds.split(cue_info_split_field)[1])
#
#                         #if boundary falls inside cue_info, move it to cue_info region mid point
#                         if cue_info_start<=adjust_boundary1<=cue_info_end:
#                             adjust_boundary1=(cue_info_start+cue_info_end)/2
#                             move_time+=((cue_info_start+cue_info_end)/2)-adjust_boundary1
#                             break
#                 s.close()
#                 new0.append(adjust_boundary1)
#                 #Write to output file
#                 if inc==1:up.write(str(round(adjust_boundary0,3))+output_split_field+str(round(adjust_boundary1,3))+text+'\n')
#                 else:up.write(str(round(new0[inc-2],3))+output_split_field+str(round(adjust_boundary1,3))+text+'\n')
#         up.close()
#     f.close()
#
#
# aeneas_sync_cue_info(output_dir + '/' + aeneas_output_file, silence_file,
#                                            output_dir + '/' + (chapter_audio.split('/')[-1]).split('.')[
#                                                0] + '_sync_adjusted.txt', input_split_field='\t', output_split_field='\t')