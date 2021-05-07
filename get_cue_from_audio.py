import struct,scipy.io.wavfile as s,argparse,glob,csv

#This does not get last line of the cue info
#Make it Automatic Does wav file contain verses or lines? by detecting the text after the times
parser = argparse.ArgumentParser(
        description='This function extracts cue info from wav files')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input dir with wav files')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output dir')
required_args.add_argument('-contains_verses', action='store_true', help='Does wav file contain verses or lines?')
required_args.add_argument('-is_wav', action='store_true', help='Files are in .wav format, otherwise mp3 is considered')


args = parser.parse_args()
input_dir=args.i[0]
output_dir=args.o[0]

print(args)

if args.is_wav:audio_type='/*.wav'
else:audio_type='/*.mp3'

def range1(start, end):
    return range(start, end+1)


def readmarkers(input_dir, mmap=False):
    for file in glob.glob(input_dir+audio_type):
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
                if file == '/Users/spanta/Desktop/jon_code_test/new_files/drive-download-20200107T220609Z-001/Udmurt_N2UDMIBT_Completed/N2_UDM_IBT_029_MRK_01_VOX.wav':
                    print(file,numcue)
                for c in range(numcue):
                    id, position, datachunkid, chunkstart, blockstart, sampleoffset = struct.unpack('<iiiiii',
                                                                                                    fid.read(24))
                    cue.append(position)
            else:
                s._skip_unknown_chunk(fid, False)
        fid.close()
        cue=[round(x/44100,3) for x in cue]

        if file=='/Users/spanta/Desktop/jon_code_test/new_files/drive-download-20200107T220609Z-001/Udmurt_N2UDMIBT_Completed/N2_UDM_IBT_029_MRK_01_VOX.wav': print(cue)
        corrected_cue=list()
        corrected_cue.append(cue[0])
        #Check values in cue info so that the cues are not misplaced
        for i in range1(1,len(cue)-1):
            if cue[i]>cue[i-1]: corrected_cue.append(cue[i])


        #Format the cue info. like aud format
        final_cue=list()
        # print(file,corrected_cue)
        for i,each_cue in enumerate(corrected_cue):

            if args.contains_verses:
                if i==0:

                    final_cue.append('0.000' + '\t' + str(each_cue) + '\t' + str(i))
                    final_cue.append(str(each_cue)+'\t'+str(corrected_cue[i+1])+'\t'+str(i+1))
                elif i>1:final_cue.append(str(corrected_cue[i-1]) + '\t' + str(each_cue)+'\t'+str(i))
            else:
                if i == 0:
                    final_cue.append('0.000' + '\t' + str(each_cue))
                else:
                    final_cue.append(str(corrected_cue[i - 1]) + '\t' + str(each_cue))

            if i<=1: print(final_cue)

        writer.writerows(zip(final_cue))
        write_file.close()
        # print(final_cue)


readmarkers(input_dir)