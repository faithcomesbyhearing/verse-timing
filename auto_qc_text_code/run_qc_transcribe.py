from transformers import Wav2Vec2ForSequenceClassification, AutoFeatureExtractor, Wav2Vec2ForCTC, AutoProcessor,logging
import torch,librosa,sys,glob,math,os,pandas as pd,json,csv,tracemalloc, textdistance,warnings,re,numpy
from numpy import random
from huggingface_hub import hf_hub_download
from torchaudio.models.decoder import ctc_decoder
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=(SettingWithCopyWarning))
logging.set_verbosity_error()
cwd=os.getcwd()
sys.path.append(cwd)
from text_normalize import normalize_text
from fuzzywuzzy import fuzz


model_id = "facebook/mms-lid-4017"
processor = AutoFeatureExtractor.from_pretrained(model_id)
model = Wav2Vec2ForSequenceClassification.from_pretrained(model_id)

audio_dir='/xyz/'
lines_csv_file='lines.csv'
#Number of audio files to use for identifying language iso code
num_audiofiles=10
#Number of audio files from which to randomly sample
total_audiofiles=20
'''
Created compatibility list steps
Extracted the mms langauges list from https://dl.fbaipublicfiles.com/mms/misc/language_coverage_mms.html , saved into a csv file called mms_languages_list.csv
Goal : Find langauge families that exist fcbh Latin based languages, for which mms trascriber model exists
Filtered fcbh language iso codes 639 which are Latin script (This is done because qc is only applied to Latin script languages
In the mms_languages_list.csv, from the excel sheet, eliminated blanks from the language_family column and only kept overlapping columns for ASR(Automatic speech recognition) and LID (Language Identification)
For mms language iso 693-3 codes which exist in fcbh iso 639 Latin script, find the mms language family 
For mms langauge family that exists in fcbh langauge family get list of mms asr iso 693-3 codes
'''
compatible_languages_list='/Users/spanta/Downloads/FCBH_QC_MMS/languages_list/final_overlap_isolist_latin_lang_family.csv'

# Detect the langauge iso code by reading random 20 audio wav files and finding the majority vote
detected_lang=list()
for each_random_number in random.randint(total_audiofiles, size=(num_audiofiles)):
    each_audio_file=glob.glob(audio_dir + '/*/*.wav')[each_random_number]
    audio_sample = librosa.load(each_audio_file, sr=16000, mono=True)[0]
    inputs = processor(audio_sample, sampling_rate=16_000, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs).logits
    lang_id = torch.argmax(outputs, dim=-1)[0].item()
    detected_lang.append(model.config.id2label[lang_id])


print(max(set(detected_lang), key = detected_lang.count))
iso_langauge_code=max(set(detected_lang), key = detected_lang.count)

# If identified language code exists in compatible_languages_list then download that model, else use english model
df = pd.read_csv(compatible_languages_list)
if df['ISO_693-3'].eq(iso_langauge_code).any():
    lang_code=iso_langauge_code
else:
    lang_code='eng'

#Download language specific model for performing audio transcribe
bin_file='adapter.'+lang_code+'.bin'
if not(os.path.isfile(os.path.join(cwd,'model',bin_file))):
    from huggingface_hub import snapshot_download
    safetensors_file='adapter.'+lang_code+'.safetensors'
    snapshot_download(repo_id="facebook/mms-1b-all",local_dir=os.path.join(cwd,'model'),allow_patterns=["adapter."+lang_code+".bin", "adapter."+lang_code+".safetensors"],local_dir_use_symlinks=False)

ASR_SAMPLING_RATE = 16_000
MODEL_ID=cwd+'/model'

# Load the model
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID,local_files_only=True)
processor.tokenizer.set_target_lang(lang_code)
model.load_adapter(lang_code)
device = torch.device("cpu")
model.to(device)

#Extract the lines from the core script using `python verse-timing-master/create_lines_from_corescript_xls.py`


# Flag lines that have missing audio file
lines_df=pd.read_csv(os.path.join(audio_dir,lines_csv_file))

#For testing in command prompt
# lines_df=pd.read_csv('/Users/spanta/Downloads/FCBH_QC_MMS/N2_BARAI/lines.csv')
# audio_dir='/Users/spanta/Downloads/FCBH_QC_MMS/BARAI_audio_files/'
# lang_code='bbb'

# Remove previous line that was recorded again , the line number contains 'r' at the end
ind=lines_df[lines_df['line_number'].astype(str).str.contains('r')].index


for each_index in ind:
    remove_line_index=each_index-1
    lines_df=lines_df.drop(index=remove_line_index)
    original_string=str(lines_df['line_number'][remove_line_index+1])
    replace_string=original_string.replace('r','')
    lines_df['line_number'][remove_line_index+1] = replace_string
updated_lines_df=lines_df


# Strings to extract line number from wav files
sub1 = "_"
sub2 = "."
sub3 = 'COR'

audio_line_numbers=list()
for audio_fp in glob.glob(audio_dir+'/*/*.wav'):
    audio_line_numbers.append((''.join((audio_fp.split(sub1)[-1].split(sub2)[0]).split(sub3)[0])).split('r')[0])

write_file=open(cwd+'QCREPORT_MISSINGLINES_'+lang_code+'.csv','a')
for each_line in updated_lines_df['line_number']:
    if str(each_line) not in audio_line_numbers :
        write_file.writelines('Missing audio for line '+str(each_line)+'\n')
write_file.close()


def write_file_header(filename,lang_code,distance_metrics):
    write_file = open(audio_dir + '/output_' + lang_code + '_'+filename+'.csv', 'a')
    string=(str(distance_metrics).replace('[','')).replace(']','')
    write_file.writelines('line_number' +','+ string+','+'transcribed_text'+','+'source_text'+'\n')
    return write_file

write_levinfile=write_file_header('levin',lang_code,['mra','fuzz_partial','levin'])
distance_list=['hamming','mlipns','levenshtein','damerau_levenshtein','jaro_winkler','jaro','strcmp95','smith_waterman','jaccard','sorensen_dice','tversky','overlap','tanimoto','cosine','monge_elkan','bag','lcsseq','lcsstr','ratcliff_obershelp','arith_ncd','rle_ncd','bwtrle_ncd','sqrt_ncd','entropy_ncd','bz2_ncd','lzma_ncd','zlib_ncd','mra','editex','prefix','postfix','length','identity','matrix','average']

write_distfile=write_file_header('all_distances',lang_code,distance_list)
write_normdistfile=write_file_header('all_normdistances',lang_code,distance_list)
write_tsnenormdistfile = write_file_header('all_tsnenormdistances', lang_code, distance_list+distance_list)

#Load wav files and transcribe
for audio_fp in glob.glob(audio_dir+'/*/*.wav'):
    print(audio_fp)
    audio_sample = librosa.load(audio_fp, sr=ASR_SAMPLING_RATE, mono=True)[0]
    inputs = processor(audio_sample, sampling_rate=ASR_SAMPLING_RATE, return_tensors="pt")
    inputs = inputs.to(device)
    with torch.no_grad():
        outputs = model(**inputs).logits
    ids = torch.argmax(outputs, dim=-1)[0]
    transcription = processor.decode(ids)
    transcription=normalize_text(transcription,lang_code)
    print('transcribed_audio:', transcription)

    #Get source text from lines.csv
    line_number = (''.join((audio_fp.split(sub1)[-1].split(sub2)[0]).split(sub3)[0])).split('r')[0]
    # text=list(df[df['line_number']==line_number]['line_content'])[0]
    text = list(updated_lines_df[updated_lines_df['line_number'] == str(line_number)]['line_content'])[0]
    normalized_text=normalize_text(text,lang_code)
    print('original_text:', normalized_text)

    #COMPUTE VARIOUS DISTANCE METRICS


    #compute just mra,fuzz partial and lavengsthein edit distance
    #Arrange lavengsthein edit distance of all strings that are 2 stdev from mean

    write_levinfile.writelines(
        str(line_number) + ',' + str(textdistance.mra.distance(transcription, normalized_text)) + ','+str(fuzz.partial_ratio(transcription, normalized_text))+',' + str(
            textdistance.levenshtein.distance(transcription,
                                              normalized_text)) + ',' + transcription + ',' + normalized_text + '\n')


    #Compute lavengsthein edit distance between words and mark words that are 2 stdev from mean



    #Compute all the distance metrics and get an average
    distance_options=['hamming','mlipns','levenshtein','damerau_levenshtein','jaro_winkler','jaro','strcmp95','smith_waterman','jaccard','sorensen_dice','tversky','overlap','tanimoto','cosine','monge_elkan','bag','lcsseq','lcsstr','ratcliff_obershelp','arith_ncd','rle_ncd','bwtrle_ncd','sqrt_ncd','entropy_ncd','bz2_ncd','lzma_ncd','zlib_ncd','mra','editex','prefix','postfix','length','identity','matrix']
    distance_options_list=distance_options
    distance_options_list.append('average')


    distance_options.pop()
    store_dist_list=list()
    for each_distance in distance_options:

        func = getattr(textdistance, each_distance)
        store_dist_list.append(func.distance(transcription, normalized_text))
    store_dist_list.append(numpy.average(store_dist_list))

    string1=str(store_dist_list)
    string1 = (str(string1).replace('[', '')).replace(']', '')


    write_distfile.writelines(
        str(line_number) + ',' + string1+',' + transcription + ',' + normalized_text + '\n')


    #Compute all the normalized distance metrics and get an average
    normdistance_options_list=distance_options
    normdistance_options_list.append('average')


    distance_options.pop()
    store_normdist_list = list()
    for each_distance in distance_options:
        func = getattr(textdistance, each_distance)
        store_normdist_list.append(func.distance(transcription, normalized_text))
    store_normdist_list.append(numpy.average(store_normdist_list))

    string2 = str(store_dist_list)
    string2 = (str(string2).replace('[', '')).replace(']', '')

    write_normdistfile.writelines(
        str(line_number) + ',' + string2 + ',' + transcription + ',' + normalized_text + '\n')


    #run tsne on both of the above numbers
    write_tsnenormdistfile.writelines(
        str(line_number) + ',' + string1+','+string2 + ',' + transcription + ',' + normalized_text + '\n')


write_levinfile.close()
write_distfile.close()
write_normdistfile.close()
write_tsnenormdistfile.close()











