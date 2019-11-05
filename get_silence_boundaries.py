def get_silence_boundaries(full_filepath,decibels=5,min_sil_len=300):
    """This function gets the silence boundaries given an input audio file
            Args:
                full_filepath (string): full path to audio file
                decibels (int or float): threshold decibel level to detect silence
                min_sil_len (int or float): minimum silence length in seconds
            Returns:
                Creates a .csv file in the directory with silence boundaries
            Comments:
                Assumes the full_filepath is in the format 'full/path/to/file'
                Ex: get_silence_boundaries('/Test/John9/B04___09_John________ENGESVN1DA.mp3',5,300)
            """
    import pydub.silence as sil,os
    from pydub import AudioSegment
    from statistics import mean

    dir=os.path.dirname(full_filepath)
    filename=full_filepath.split('/')[-1]
    sound = AudioSegment.from_mp3(full_filepath)
    dBFS = sound.dBFS
    silence_boundaries = sil.detect_silence(sound, min_silence_len=min_sil_len, silence_thresh=dBFS - decibels)
    if os.path.exists(dir+'/'+filename+'_silence.csv'): os.remove(dir+'/'+filename+'_silence.csv')
    silence_file=open(dir+'/'+filename+'_silence.csv','w')
    silence_file.write('# -'+str(decibels)+','+str(min_sil_len)+'\n')
    line_inc=0
    for boundaries in silence_boundaries:
        line_inc+=1
        boundaries=[x/1000 for x in boundaries]
        silence_file.write("{0},{1},{2}\n".format(line_inc,boundaries[0],boundaries[1]))
        print("{0} {1} silence".format(boundaries[0],boundaries[1]))
    silence_file.close()
