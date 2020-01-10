import struct,scipy.io.wavfile as s,argparse,glob,csv

parser = argparse.ArgumentParser(
        description='This function extracts cue info from wav files')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input dir with wav files')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output dir')

args = parser.parse_args()
input_dir=args.i[0]
output_dir=args.o[0]

def range1(start, end):
    return range(start, end+1)


def readmarkers(input_dir, mmap=False):

    for file in glob.glob(input_dir+'*.wav'):

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
        #Check values in cue info so that the cues are not misplaced
        for i in range1(1,len(cue)-1):
            if cue[i]>cue[i-1]: corrected_cue.append(cue[i])


        #Format the cue info. like aud format
        final_cue=list()
        for i,each_cue in enumerate(corrected_cue):
            if i==0: final_cue.append('0.000'+'\t'+str(each_cue))
            else:final_cue.append(str(corrected_cue[i-1]) + '\t' + str(each_cue))

        writer.writerows(zip(final_cue))
        write_file.close()
        print(final_cue)


readmarkers(input_dir)
