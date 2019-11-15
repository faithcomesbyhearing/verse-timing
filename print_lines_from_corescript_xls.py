
''' This function reads a core script and print line and verse info. of target language

EX run:
python3 /Users/spanta/Desktop/jon_code_test/upload_code/print_lines.py -i /Users/spanta/Desktop/jon_code_test/XLScr1051m_N_eng__English_N2_ESV__02.xls -o /Users/spanta/Desktop/jon_code_test/upload_code/test.csv -fileset 'ENG_N2' -book_chapter 'JOHN 9'
python3  /Users/spanta/Desktop/jon_code_test/upload_code/print_lines.py -i /Users/spanta/Desktop/jon_code_test/CORE_Scr_1061m_NT_1ENG__25_Spkr__Hindi_N2_HIN_WTC.xls -o /Users/spanta/Desktop/jon_code_test/upload_code/test.csv -fileset 'ENG_N2' -book_chapter 'JOHN 9'
python3  /Users/spanta/Desktop/jon_code_test/upload_code/print_lines.py -i /Users/spanta/Desktop/jon_code_test/CORE_Scr_1064u01_NT_1Eng__Virtual__Telugu_N2_TCW_WTC.xls -o /Users/spanta/Desktop/jon_code_test/upload_code/test.csv -fileset 'ENG_N2' -book_chapter 'JOHN 9'
Check out Sample results at the bottom of this code
Side note: Dont find verses just based on numbers because numbers like 144,000 and verse # at 666
'''

import argparse,re,pandas as pd,os

parser = argparse.ArgumentParser(
        description='This function creates lines.csv file from core script .xls file')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
    '-i', required=True, nargs=1, type=str, help='Input core script .xls file')
required_args.add_argument(
    '-o', required=True, nargs=1, type=str, help='Output file name')
required_args.add_argument('-fileset', nargs=1, type=str,default='[0]',help='custom fileset id')

optional_args=parser.add_argument_group('optional arguments')
optional_args.add_argument('-sheetname', nargs=1, default=[0],type=int,help='sheetname or # in corescript')
optional_args.add_argument('-book_chapter', nargs=1, type=str, default=['MATTHEW 1'],help='custom book chapter. Be sure to include the space. EX: John 9')
optional_args.add_argument('-noheader', action='store_true', help='Remove header: fileset,book,chapter,db,sId,sBegin,sEnd')
optional_args.add_argument('-find_string', nargs=1, type=str,default=['MATTHEW CHP 1'],help='string to find input langauge column index in corescript. Default:MATTHEW CHP 1')
optional_args.add_argument('-target_pointer', nargs=1, type=str,default='2',help='Integer to add to input language column index to get target language in corescript. '
                                                                                 'Default: find_string column index + 2')
optional_args.add_argument('-line_pointer', nargs=1, type=int,default='-2',help='Integer to add to input language column index to get line number in corescript. '
                                                                                'Default: find_string column index - 2')


args = parser.parse_args()
print(args)
input_file=args.i[0]
output_file=args.o[0]
fileset=args.fileset[0]

core_script_sheet_name=args.sheetname[0]
if args.book_chapter is not None: book_chapter=args.book_chapter[0]
find_string=args.find_string[0]
target_pointer=int(args.target_pointer[0])
line_num_pointer=args.line_pointer

#custom tags
combine_tag='DO NOT COMBINE'

# Get the first column index of line numbers, input language, target language and corescript dataframe
def get_column_indexes_from_corescript(input_file=input_file,core_script_sheet_name=core_script_sheet_name,find_string=find_string,target_pointer=target_pointer):
    # Open read and write files
    df=(pd.read_excel(input_file,sheet_name=core_script_sheet_name,encoding = 'utf-8')).astype(str)
    for c in range(0,len(df.columns)):
        for r in range(0, len(df)):
            if (df.iloc[r,c]).__contains__(find_string)==True:
                # print(df.iloc[r,c])
                input_language_column_index=c
                line_column_index=c+line_num_pointer
                target_language_column_index=c+target_pointer
                # print(c,c+target_pointer)
                break
    return line_column_index,input_language_column_index,target_language_column_index,df

def flatten(l):
    flatList = []
    for elem in l:
        # if an element of a list is a list
        # iterate over this list and add elements to flatList
        if type(elem) == list:
            for e in elem:
                flatList.append(e)
        else:
            flatList.append(elem)
    return flatList

def range1(start, end):
    return range(start, end+1)

def get_chapter_phrases(book_chapter,target_language_column_index,script_df):
    # Get indices of chapter text from heading to end line
    line_start_index=0
    line_end_index=0
    book_chapter=book_chapter.strip()
    book=book_chapter.split(' ')[0]
    chapter=int(book_chapter.split(' ')[1])
    input_book_chapter=(book+' '+'CHP'+' '+str(chapter)).upper()

    input_column_name=script_df.columns[input_language_column_index]
    target_column_name=script_df.columns[target_language_column_index]
    line_column_name=script_df.columns[line_column_index]

    locations=(script_df[input_column_name].str).contains(input_book_chapter)==True
    for i in range(0,len(locations)):
        if locations[i]==True:
            line_start_index=i
            break

    output_book_chapter=(book+' '+'CHP'+' '+str(chapter+1)).upper()
    locations=(script_df[input_column_name].str).contains(output_book_chapter)==True
    for i in range(0,len(locations)):
        if locations[i]==True:
            line_end_index=i-1
            break



    new = dict()
    current_verse_num=0
    mark_words=dict()


    #Process chapter heading separately
    # Extract line info.
    line_num = (script_df[line_column_name][line_start_index]).split('.')[0]

    # Extract cues from input language section
    do_not_combine_boolean_flag = (script_df[input_column_name][line_start_index]).__contains__(
        combine_tag.upper())
    # IMP: assumes the timing cues are inside the || string
    if (script_df[input_column_name][line_start_index]).__contains__('|'):
        postSilence = ''.join(filter(str.isdigit, re.split('\|+', script_df[input_column_name][line_start_index])[1]))
    else:
        postSilence = ''

    print("line_number:{0},line_content:{1},verses_in_current_line:{4},postSilence:{2},do_not_combine_flag:{3}".format(
        line_num, script_df[target_column_name][line_start_index], postSilence, do_not_combine_boolean_flag, ''))

    # For each line in chapter process and print the same info. as above
    for index in range1(line_start_index+1,line_end_index):


        # Extract line info.
        line_num=(script_df[line_column_name][index]).split('.')[0]

        #Extract cues from input language section
        do_not_combine_boolean_flag = (script_df[input_column_name][index]).__contains__(
            combine_tag.upper())
        # IMP: assumes the timing cues are inside the || string
        if (script_df[input_column_name][index]).__contains__('|'):
            postSilence=''.join(filter(str.isdigit,re.split('\|+',script_df[input_column_name][index])[1]))
        else:
            postSilence = ''


        #Extract info. from target language section

        line_content=(script_df[target_column_name][index]).split()

        verse_num_list=list()
        verse_ind_list=list()

        for i,check_word in enumerate(line_content):
            if check_word.isdigit() and int(check_word) <= 119:
                 verse_number = int(check_word)
                 verse_num_list.append(verse_number)
                 verse_ind_list.append(i)
                 current_verse_num=verse_number
            elif re.search('{(.*)}', check_word) is not None and int(re.search('{(.*)}', check_word).group(1))<=119:
                 verse_number = int(re.search('{(.*)}', check_word).group(1))
                 verse_num_list.append(verse_number)
                 verse_ind_list.append(i)
                 current_verse_num=verse_number
            elif i==0:
                verse_num_list.append(current_verse_num)

        print("line_number:{0},line_content:{1},verses_in_current_line:{4},postSilence:{2},do_not_combine_flag:{3}".format(line_num,script_df[target_column_name][index],postSilence,do_not_combine_boolean_flag,verse_num_list))






line_column_index,input_language_column_index,target_language_column_index,script_df=get_column_indexes_from_corescript()
print("line_column_name:{0},input_language_column_name:{1},target_language_column_name:{2}".format(script_df.columns[line_column_index],script_df.columns[input_language_column_index],script_df.columns[target_language_column_index]))

write_file=open(output_file,'w')
# Write header as requested by user
if not(args.noheader):write_file.write('fileset,book,chapter,phrase_content,phrase_counter,verse_number,line_number,characters,words,postSilence,do_not_combine_boolean_flag\n')

get_chapter_phrases(book_chapter,target_language_column_index,script_df)

'''
python3 /Users/spanta/Desktop/jon_code_test/upload_code/print_lines.py -i /Users/spanta/Desktop/jon_code_test/XLScr1051m_N_eng__English_N2_ESV__02.xls -o /Users/spanta/Desktop/jon_code_test/upload_code/test.csv -fileset 'ENG_N2' -book_chapter 'JOHN 9'
Namespace(book_chapter=['JOHN 9'], fileset=['ENG_N2'], find_string=['MATTHEW CHP 1'], i=['/Users/spanta/Desktop/jon_code_test/XLScr1051m_N_eng__English_N2_ESV__02.xls'], line_pointer=-2, noheader=False, o=['/Users/spanta/Desktop/jon_code_test/upload_code/test.csv'], sheetname=[0], target_pointer='2')
line_column_name:Unnamed: 8,input_language_column_name:2018-07-18 14:16:45,target_language_column_name:ENGLISH           N2ESV
line_number:2589,line_content: JOHN 9,verses_in_current_line:,postSilence:,do_not_combine_flag:False
line_number:2590,line_content: 1 As he passed by, he saw a man blind from birth. 2 And his disciples asked him, ,verses_in_current_line:[1, 2],postSilence:,do_not_combine_flag:False
line_number:2591,line_content: “Rabbi, who sinned, this man or his parents, that he was born blind?” ,verses_in_current_line:[2],postSilence:,do_not_combine_flag:False
line_number:2592,line_content: 3 Jesus answered, ,verses_in_current_line:[3],postSilence:,do_not_combine_flag:False
line_number:2593,line_content: “It was not that this man sinned, or his parents, but that the works of God might be displayed in him. 4 We must work the works of him who sent me while it is day; night is coming, when no one can work. 5 As long as I am in the world, I am the light of the world.” ,verses_in_current_line:[3, 4, 5],postSilence:,do_not_combine_flag:False
line_number:2594,line_content: 6 Having said these things, he spat on the ground and made mud with the saliva. Then he anointed the man’s eyes with the mud 7 and said to him, ,verses_in_current_line:[6, 7],postSilence:,do_not_combine_flag:False
line_number:2595,line_content: “Go, wash in the pool of Siloam” ,verses_in_current_line:[7],postSilence:,do_not_combine_flag:False
line_number:2596,line_content: (which means Sent). So he went and washed and came back seeing. 8 The neighbors and those who had seen him before as a beggar were saying, ,verses_in_current_line:[7, 8],postSilence:,do_not_combine_flag:False
line_number:2597,line_content: “Is this not the man who used to sit and beg?” ,verses_in_current_line:[8],postSilence:,do_not_combine_flag:False
line_number:2598,line_content: 9 Some said, ,verses_in_current_line:[9],postSilence:,do_not_combine_flag:False
line_number:2599,line_content: “It is he.” ,verses_in_current_line:[9],postSilence:,do_not_combine_flag:False
line_number:2600,line_content: Others said, ,verses_in_current_line:[9],postSilence:,do_not_combine_flag:False
line_number:2601,line_content: “No, but he is like him.” ,verses_in_current_line:[9],postSilence:,do_not_combine_flag:False
line_number:2602,line_content: He kept saying, ,verses_in_current_line:[9],postSilence:,do_not_combine_flag:False
line_number:2603,line_content: “I am the man.” ,verses_in_current_line:[9],postSilence:,do_not_combine_flag:False
line_number:2604,line_content: 10 So they said to him, ,verses_in_current_line:[10],postSilence:,do_not_combine_flag:False
line_number:2605,line_content: “Then how were your eyes opened?” ,verses_in_current_line:[10],postSilence:,do_not_combine_flag:False
line_number:2606,line_content: 11 He answered, ,verses_in_current_line:[11],postSilence:,do_not_combine_flag:False
line_number:2607,line_content: “The man called Jesus made mud and anointed my eyes and said to me, ‘Go to Siloam and wash.’ So I went and washed and received my sight.” ,verses_in_current_line:[11],postSilence:,do_not_combine_flag:False
line_number:2608,line_content: 12 They said to him, ,verses_in_current_line:[12],postSilence:,do_not_combine_flag:False
line_number:2609,line_content: “Where is he?” ,verses_in_current_line:[12],postSilence:,do_not_combine_flag:False
line_number:2610,line_content: He said, ,verses_in_current_line:[12],postSilence:,do_not_combine_flag:False
line_number:2611,line_content: “I do not know.”,verses_in_current_line:[12],postSilence:,do_not_combine_flag:False
line_number:2612,line_content: 13 They brought to the Pharisees the man who had formerly been blind. 14 Now it was a Sabbath day when Jesus made the mud and opened his eyes. 15 So the Pharisees again asked him how he had received his sight. And he said to them, ,verses_in_current_line:[13, 14, 15],postSilence:,do_not_combine_flag:False
line_number:2613,line_content: “He put mud on my eyes, and I washed, and I see.” ,verses_in_current_line:[15],postSilence:,do_not_combine_flag:False
line_number:2614,line_content: 16 Some of the Pharisees said, ,verses_in_current_line:[16],postSilence:,do_not_combine_flag:False
line_number:2615,line_content: “This man is not from God, for he does not keep the Sabbath.” ,verses_in_current_line:[16],postSilence:,do_not_combine_flag:False
line_number:2616,line_content: But others said, ,verses_in_current_line:[16],postSilence:,do_not_combine_flag:False
line_number:2617,line_content: “How can a man who is a sinner do such signs?”,verses_in_current_line:[16],postSilence:,do_not_combine_flag:False
line_number:2618,line_content:  And there was a division among them. 17 So they said again to the blind man, ,verses_in_current_line:[16, 17],postSilence:,do_not_combine_flag:False
line_number:2619,line_content: “What do you say about him, since he has opened your eyes?” ,verses_in_current_line:[17],postSilence:,do_not_combine_flag:False
line_number:2620,line_content: He said, ,verses_in_current_line:[17],postSilence:,do_not_combine_flag:False
line_number:2621,line_content: “He is a prophet.”,verses_in_current_line:[17],postSilence:,do_not_combine_flag:False
line_number:2622,line_content: 18 The Jews did not believe that he had been blind and had received his sight, until they called the parents of the man who had received his sight 19 and asked them, ,verses_in_current_line:[18, 19],postSilence:,do_not_combine_flag:False
line_number:2623,line_content: “Is this your son, who you say was born blind? How then does he now see?” ,verses_in_current_line:[19],postSilence:,do_not_combine_flag:False
line_number:2624,line_content: 20 His parents answered, ,verses_in_current_line:[20],postSilence:,do_not_combine_flag:False
line_number:2625,line_content: “We know that this is our son and that he was born blind. ,verses_in_current_line:[20],postSilence:,do_not_combine_flag:False
line_number:2626,line_content: 21 But how he now sees we do not know, nor do we know who opened his eyes. Ask him; he is of age. He will speak for himself.” ,verses_in_current_line:[21],postSilence:,do_not_combine_flag:False
line_number:2627,line_content: 22(His parents said these things because they feared the Jews, for the Jews had already agreed that if anyone should confess Jesus  to be Christ, he was to be put out of the synagogue.) 23 Therefore his parents said, “He is of age; ask him.” 24 So for the second time they called the man who had been blind and said to him, ,verses_in_current_line:[21, 23, 24],postSilence:,do_not_combine_flag:False
line_number:2628,line_content: “Give glory to God. We know that this man is a sinner.” ,verses_in_current_line:[24],postSilence:,do_not_combine_flag:False
line_number:2629,line_content: 25 He answered, ,verses_in_current_line:[25],postSilence:,do_not_combine_flag:False
line_number:2630,line_content: “Whether he is a sinner I do not know. One thing I do know, that though I was blind, now I see.” ,verses_in_current_line:[25],postSilence:,do_not_combine_flag:False
line_number:2631,line_content: 26 They said to him, ,verses_in_current_line:[26],postSilence:,do_not_combine_flag:False
line_number:2632,line_content: “What did he do to you? How did he open your eyes?” ,verses_in_current_line:[26],postSilence:,do_not_combine_flag:False
line_number:2633,line_content: 27 He answered them, ,verses_in_current_line:[27],postSilence:,do_not_combine_flag:False
line_number:2634,line_content: “I have told you already, and you would not listen. Why do you want to hear it again? Do you also want to become his disciples?” ,verses_in_current_line:[27],postSilence:,do_not_combine_flag:False
line_number:2635,line_content: 28 And they reviled him, saying, ,verses_in_current_line:[28],postSilence:,do_not_combine_flag:False
line_number:2636,line_content: “You are his disciple, but we are disciples of Moses. 29 We know that God has spoken to Moses, but as for this man, we do not know where he comes from.” ,verses_in_current_line:[28, 29],postSilence:,do_not_combine_flag:False
line_number:2637,line_content: 30 The man answered, ,verses_in_current_line:[30],postSilence:,do_not_combine_flag:False
line_number:2638,line_content: “Why, this is an amazing thing! You do not know where he comes from, and yet he opened my eyes. 31 We know that God does not listen to sinners, but if anyone is a worshiper of God and does his will, God listens to him. 32 Never since the world began has it been heard that anyone opened the eyes of a man born blind. 33 If this man were not from God, he could do nothing.” ,verses_in_current_line:[30, 31, 32, 33],postSilence:,do_not_combine_flag:False
line_number:2639,line_content: 34 They answered him, ,verses_in_current_line:[34],postSilence:,do_not_combine_flag:False
line_number:2640,line_content: “You were born in utter sin, and would you teach us?” ,verses_in_current_line:[34],postSilence:,do_not_combine_flag:False
line_number:2641,line_content: And they cast him out. 35 Jesus heard that they had cast him out, and having found him he said, ,verses_in_current_line:[34, 35],postSilence:,do_not_combine_flag:False
line_number:2642,line_content: “Do you believe in the Son of Man?”  ,verses_in_current_line:[35],postSilence:,do_not_combine_flag:False
line_number:2643,line_content: 36 He answered, ,verses_in_current_line:[36],postSilence:,do_not_combine_flag:False
line_number:2644,line_content: “And who is he, sir, that I may believe in him?” ,verses_in_current_line:[36],postSilence:,do_not_combine_flag:False
line_number:2645,line_content: 37 Jesus said to him, ,verses_in_current_line:[37],postSilence:,do_not_combine_flag:False
line_number:2646,line_content: “You have seen him, and it is he who is speaking to you.” ,verses_in_current_line:[37],postSilence:,do_not_combine_flag:False
line_number:2647,line_content: 38 He said, ,verses_in_current_line:[38],postSilence:,do_not_combine_flag:False
line_number:2648,line_content: “Lord, I believe,”,verses_in_current_line:[38],postSilence:,do_not_combine_flag:False
line_number:2649,line_content:  and he worshiped him. 39 Jesus said,,verses_in_current_line:[38, 39],postSilence:,do_not_combine_flag:False
line_number:2650,line_content:  “For judgment I came into this world, that those who do not see may see, and those who see may become blind.” ,verses_in_current_line:[39],postSilence:,do_not_combine_flag:False
line_number:2651,line_content: 40 Some of the Pharisees near him heard these things, and said to him, ,verses_in_current_line:[40],postSilence:,do_not_combine_flag:False
line_number:2652,line_content: “Are we also blind?” ,verses_in_current_line:[40],postSilence:,do_not_combine_flag:False
line_number:2653,line_content: 41 Jesus said to them, ,verses_in_current_line:[41],postSilence:,do_not_combine_flag:False
line_number:2654,line_content: “If you were blind, you would have no guilt;  but now that you say, ‘We see,’your guilt remains.,verses_in_current_line:[41],postSilence:2,do_not_combine_flag:False
'''