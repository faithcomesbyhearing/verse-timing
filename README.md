# verse-timing

Aeneas Algorithm

The way aeneas works is to synthesize each phrase using a text-to-speech engine, and then compare the synthesized audio files against the input audio file to find the phrase breaks. To do this, a lot of clever mathematical computation goes on behind the scenes: Using the Sakoe-Chiba Band Dynamic Time Warping (DTW) algorithm to align the Mel-frequency cepstral coefficients (MFCCs) representation of the given (real) audio wave and the audio wave obtained by synthesizing the text fragments with a TTS engine, eventually mapping the computed alignment back onto the (real) time domain.


https://github.com/readbeyond/aeneas/blob/master/wiki/HOWITWORKS.md

compute MFCC from real and synthesized audio
Next, we compute an abstract matrix representation for each of the two audio signals R and S, called Mel-frequency cepstral coefficients (MFCC).
The MFCC capture the overall "shape" of the audio signal, neglecting local details like the color of the voice.
After this step, we have two new objects:
the MFCC_R matrix, of size (k, n), containing the MFCC coefficients for the real audio file R;
the MFCC_S matrix, of size (k, m), containing the MFCC coefficients for the synthesized audio file S.
Each column of the matrix, also called frame, corresponds to a sub-interval of the audio file, all with the same length, for example 40 milliseconds. So, if the audio file R has length 10 seconds, MFCC_R will have 250 columns, the first corresponding to the interval between 0.000 and 0.040, the second corresponding to the interval [0.040, 0.080], and so on. Since in general the audio files R and S have different lengths, the corresponding MFCC_R and MFCC_S matrices will have a different number of columns, let's say n and m respectively.
Both matrices have k rows, each representing one MFCC coefficient. The first coefficient (row 0) of each frame represents the spectral log power of the audio in that frame.
For both R and S, we can map a time instant in the audio file to the corresponding frame index in MFCC_R or MFCC_S. Moreover, we can map back a frame index in MFCC_R or MFCC_S to the corresponding interval in R or S.
compute DTW
The next step consists in computing the DTW between the two MFCC matrices.
First, a cost matrix COST of size (n, m) is computed by taking the dot product * of the two MFCC matrices:
COST[i][j] = MFCC_R[:][i] * MFCC_S[:][j]

Then, the DTW algorithm is run over the cost matrix to find the minimum cost path transforming S into R.
Since computing this algorithm over the full matrix would be too expensive, requiring space (memory) and time Theta(nm), only a stripe (band) around the main diagonal is computed, and the DTW path is constrained to stay inside this stripe. The width d of the stripe, the so-called margin, is a parameter adjusting the tradeoff between the "quality" of the approximation produced and the space/time Theta(nd) to produce it.

This approach is called Sakoe-Chiba Band (approximation of the exact) Dynamic Time Warping, because, in general, the produced path is not the minimum cost path, but only an approximation of it. However, given the particular structure of the forced alignment task, the Sakoe-Chiba approximation often returns the optimal solution, when the margin d is set suitably large to "absorb" the variation of speed between the real audio and the synthesized audio, but small enough to make the computation fast enough.
The output of this step is a synt-frame-index-to-real-frame-index map M2, which associates a column index in MFCC_R to each column index in MFCC_S. In other words, it maps the synthesized time domain back onto the real time domain. In our example:
M2 = [
    0  -> 10
    1  -> 11
    2  -> 12
    3  -> 14
    ...
    15 -> 66
    16 -> 67
    ...
    m  -> n
]

Thanks to the implicit frame-index-to-audio-time correspondence, the M2 map can be viewed as mapping intervals in the synthesized audio into intervals of the real audio:
M2 = [
    [0.000, 0.040] -> [0.000, 0.440]
    [0.040, 0.080] -> [0.480, 0.520]
    [0.080, 0.120] -> [0.520, 0.560]
    [0.120, 0.160] -> [0.600, 0.640]
    ...
    [0.600, 0.640] -> [2.640, 2.680]
    [0.640, 0.680] -> [2.680, 2.720]
    ...
]

Step 5: mapping back to the real time domain
The last step consists in composing the two maps M2 and M1, obtaining the desired map M that associates each text fragment f to the corresponding interval in the real audio file:
M[f] = [ M2[(M1[f].begin)].begin, M2[(M1[f].end)].begin ]

Continuing our example, for the first text fragment we have:
f      = f_1                # "Sonnet 1"

M1[f]  = [0.000, 0.638]     # in the synthesized audio
       = [0, 15]            # as MFCC_S indices

M2[0]  = 0                  # as MFCC_R index
       = [0.000, 0.040]     # as interval in the real audio
M2[15] = 66                 # as MFCC_R index
       = [2.640, 2.680]     # as interval in the real audio

M[f_1] = [0.000, 2.640]     # in the real audio

Repeating the above for each fragment, we obtain the map M for the entire text:
M = [
    "Sonnet I"                                       -> [ 0.000,  2.640]
    "From fairest creatures we desire increase,"     -> [ 2.640,  5.880]
    "That thereby beauty's rose might never die,"    -> [ 5.880,  9.240]
    "But as the riper should by time decease,"       -> [ 9.240, 11.920]
    "His tender heir might bear his memory:"         -> [11.920, 15.280]
    ...
    "To eat the world's due, by the grave and thee." -> [48.080, 53.240]
]


NOTE: The final output map M has time values which are multiples of the MFCC frame size (MFCC window shift), for example 40 milliseconds in the example above. This effect is due to the discretization of the audio signal. The user can reduce this effect by setting a smaller MFCC window shift, say to 5 milliseconds, at the cost of increasing the demand of computation resources (memory and time). The default settings of aeneas are fine for aligning audio and text when the text fragments have paragraph, sentence, or sub-sentence granularity. For word-level granularity, the user might want to decrease the MFCC window shift parameter. Please consult the Command Line Tutorial in the documentation for further advice.

https://rtavenar.github.io/hdr/parts/01/dtw.html
https://pyts.readthedocs.io/en/stable/auto_examples/metrics/plot_sakoe_chiba.html




Tools to determine the start time of verses in chapter audio files. Please install the required modules for the code to work. Download the requirements.txt file from this repo and do : pip install -r requirements.txt
IDE Used: PyCharm Community Edition 2018.3 (Free) 


batch*.py scripts are used to run the code through a list of given langauges,filsetids,corescripts,qinfo files. They run the following code:
1)Extract lines and verses from corescript
2)Extract verse timings using aeneas package in adobe audtion format
3)Extract line and verse timings in SAB format
4)Extract line timnings from .clt files(qinfo)
5)Compute quality control metric by comparing the line timings computed using the aeneas process vs line timings from qinfo, to ,make sure its within reasonable agreement. The qinfo files : line timings are only used as a method for Quality control rather than extracting verse timings from them because they may not reflect the latest edits done by the audio processing team. Hence the audio and qinfo line timings may not match up as expected. We use aeneas package to extract verse boundaries.
6)Upload timnings to Database and create hls streams


The following info. is related to running code specific to a language. Ex: Chinanteco. The batch code is being updated to accomodate new use cases as each language has various new cases it presents: ex: Differences in core script text, parsing different columns, non-standard naming conventions, parsing verse numbers with various wild cards, chapter headings, naming conventions of audio files, Database entries etc. 

Tested to work with exact command line arguments, input files naming convention on Mark gospel for Chinanteco and having line cue info markers text files as shown below. 

The foll. cue info files are manually extracted from clt tool and written in text format. The compare_with_cue_info_chinanteco.py code wont run if it can't find these files in the output dir. Please unzip "Chinanteco_cue_info_text_files.zip" uploaded to github as below.  
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.029.MRC.01_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.030.MRC.02_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.031.MRC.03_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.032.MRC.04_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.033.MRC.05_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.034.MRC.06_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.035.MRC.07_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.036.MRC.08_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.037.MRC.09_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.038.MRC.10_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.039.MRC.11_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.040.MRC.12_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.041.MRC.13_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.042.MRC.14_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.043.MRC.15_cue_info.txt
/Users/spanta/Desktop/jon_code_test/upload_code/chinanteco_aeneas/lang_code_epo/N2.CLE.TBL.044.MRC.16_cue_info.txt

Place the cue info. files in the output directory. Ex: /Users/spanta/Documents/FCBH_github/outputs


Input files:
ls /Users/spanta/Desktop/jon_code_test/new_files/drive-download-20200107T220609Z-001/Chinanteco_San_Juan_Lealao_N2CLETBL
CORE_Scr_1059r_NT_1ENG__25_Rdr__Chinanteco_de_San_Juan_Lealao_N1_CLE_TBL.xls	N2_CLE_TBL_0037_MRC_09.wav
N2_CLE_TBL_0029_MRC_01.wav							N2_CLE_TBL_0038_MRC_10.wav
N2_CLE_TBL_0030_MRC_02.wav							N2_CLE_TBL_0039_MRC_11.wav
N2_CLE_TBL_0031_MRC_03.wav							N2_CLE_TBL_0040_MRC_12.wav
N2_CLE_TBL_0032_MRC_04.wav							N2_CLE_TBL_0041_MRC_13.wav
N2_CLE_TBL_0033_MRC_05.wav							N2_CLE_TBL_0042_MRC_14.wav
N2_CLE_TBL_0034_MRC_06.wav							N2_CLE_TBL_0043_MRC_15.wav
N2_CLE_TBL_0035_MRC_07.wav							N2_CLE_TBL_0044_MRC_16.wav
N2_CLE_TBL_0036_MRC_08.wav

Example code to run Chinanteco. 

python3.7 /Users/spanta/Documents/FCBH_github/create_lines_from_corescript_xls.py -i /Users/spanta/Documents/FCBH_github/Chinanteco_inputs/CORE_Scr_1059r_NT_1ENG__25_Rdr__Chinanteco_de_San_Juan_Lealao_N1_CLE_TBL.xls -o /Users/spanta/Documents/FCBH_github/outputs/lines.csv -book Mark


Info. about input arguments
parser = argparse.ArgumentParser(
        description='This function creates lines.csv file from core script .xls file')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input core script .xls file')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output file name')
required_args.add_argument('-fileset', nargs=1, type=str,default=['test'],help='custom fileset id')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-sheetname', nargs=1, default=[0],type=int,help='sheetname or # in corescript')
optional_args.add_argument('-book', nargs=1, type=str,help='custom book.EX: Mark')
optional_args.add_argument('-book_chapter', nargs=1, type=str, default=['MATTHEW 1'],help='custom book chapter. Be sure to include the space. EX: John 9')
optional_args.add_argument('-noheader', action='store_true', help='Remove header: fileset,book,chapter,db,sId,sBegin,sEnd')
optional_args.add_argument('-find_string', nargs=1, type=str,default=['MATTHEW CHP 1'],help='string to find input langauge column index in corescript. Default:MATTHEW CHP 1')
optional_args.add_argument('-target_pointer', nargs=1, type=str,default=['2'],help='Integer to add to input language column index to get target language in corescript. '
                                                                                 'Default: find_string column index + 2')
optional_args.add_argument('-line_pointer', nargs=1, type=str,default=['-2'],help='Integer to add to input language column index to get line number in corescript. '
                                                                                'Default: find_string column index - 2')

------------------------


python3 /Users/spanta/Documents/FCBH_github/create_aeneas.py -input_lines_csv /Users/spanta/Documents/FCBH_github/outputs/lines.csv -input_audio_dir /Users/spanta/Documents/FCBH_github/Chinanteco_inputs -output_dir /Users/spanta/Documents/FCBH_github/outputs -language_code epo -sound_find_string MRC -move_adjustment -write_audition_format


Info. about input arguments

parser = argparse.ArgumentParser(
        description='This function creates lines.csv file from core script .xls file. Assumes lines.csv has header')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-input_lines_csv', required=True, nargs=1, type=str, help='Input excel which contains lines.csv')
required_args.add_argument(
    '-input_audio_dir', required=True, nargs=1, type=str, help='Input directory that contains chapter audio mp3s')
required_args.add_argument(
    '-output_dir', required=True, nargs=1, type=str, help='Output directory to store aeneas.csv files')
required_args.add_argument(
    '-language_code', required=True, nargs=1, type=str, help='3 letter Language code to use for aeneas')


optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-sound_find_string', nargs=1, type=str,help='EX: MRK to get MRK1,ESV_MRK_01 etc.')
optional_args.add_argument('-book_chapter', nargs=1, type=str, default=['MATTHEW 1'],help='custom book chapter. Be sure to include the space. EX: John 9')
optional_args.add_argument('-noheader', action='store_true', help='Remove header: fileset,book,chapter,line#,verse#,verse_content,time')
optional_args.add_argument('-no_audacity_output', action='store_true', help='Remove header: fileset,book,chapter,line#,verse#,verse_content,time')
optional_args.add_argument('-input_no_header', action='store_true', help='Indicate whether input lines.csv has header or not')
optional_args.add_argument('-adjust_silence', action='store_true', help='Adjust boundaries with closest silence midpoint')
optional_args.add_argument('-move_adjustment', action='store_true', help='Move time points as you adjust for silence')
optional_args.add_argument('-write_audition_format', action='store_true', help='Write output to audition tab csv format')

------------

python3 /Users/spanta/Documents/FCBH_github/compare_with_cue_info_chinanteco.py -i /Users/spanta/Documents/FCBH_github/outputs -o /Users/spanta/Documents/FCBH_github/outputs -book_find_string MRC -synced_silence -write_audition_format -print_chapter 3 -extract_verse_timing

Info. about input arguments

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

batch_create_lines_from_db_bible_verses.py:Added feature to create verse timings from bible_verses from DB
Bible verses do not have chapter headings. So I transcribe the audio file and extract the text using silence regions to fill the chapter headings.
