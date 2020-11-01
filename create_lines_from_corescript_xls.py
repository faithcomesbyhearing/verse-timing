
''' This function reads a core script and creates line and verse info. of target language

EX run:
python3 create_lines_from_corescript_xls.py -i /Users/spanta/Desktop/jon_code_test/XLScr1051m_N_eng__English_N2_ESV__02.xls -o ENG_lines.csv -fileset 'ENG_N2'
python3 create_lines_from_corescript_xls.py -i /Users/spanta/Desktop/jon_code_test/XLScr1051m_N_eng__English_N2_ESV__02.xls -o ENG_lines.csv -fileset 'ENG_N2' -book_chapter 'JOHN 9'
Side note: Dont find verses just based on numbers because numbers like 144,000 and verse # at 666

Notes:
#Default starting book chapter is MATTHEW 1, change this if it includes Old testament
# Play with ! "" and other punctuation marks if it makes any difference to aeneas
'''

import argparse,re,pandas as pd,os,csv
from num2words import num2words
from langdetect import detect


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
optional_args.add_argument('-target_pointer', nargs=1, type=str,default=['1'],help='Integer to add to input language column index to get target language in corescript. '
                                                                                 'Default: find_string column index + 2')
optional_args.add_argument('-line_pointer', nargs=1, type=str,default=['-3'],help='Integer to add to input language column index to get line number in corescript. '
                                                                                'Default: find_string column index - 2')


args = parser.parse_args()
print(args)
input_file=args.i[0]
output_file=args.o[0]
fileset=args.fileset[0]

core_script_sheet_name=args.sheetname[0]
#if args.book_chapter is not None: book_chapter=args.book_chapter[0]
if args.book is not None:
    book=(str(args.book[0])).lower()
else:book=None
find_string=args.find_string[0]
# if args.target_pointer is not None:
target_pointer=int(args.target_pointer[0])
# if args.line_pointer is not None:
line_num_pointer=int(args.line_pointer[0])

#custom tags
combine_tag='DO NOT COMBINE'
line_gap_silence=0.5
verses_split_string='-'
chapter_find_string='CHP'

write_file_handle=open(output_file,'w',encoding='utf-8')
write_file = csv.writer(write_file_handle)
# Write header as requested by user
if not(args.noheader):write_file.writerow(('fileset','book','chapter','line_number', 'verse_number','verse_content','words','characters','postSilence_secs_cue','expected_post_silence_secs','do_not_combine_boolean_flag'))



# Get the first column index of line numbers, input language, target language and corescript dataframe
def get_column_indexes_from_corescript(input_file=input_file,core_script_sheet_name=core_script_sheet_name,find_string=find_string,target_pointer=target_pointer):
    line_column_index=8
    input_language_column_index=10
    target_language_column_index=12
    # Open read and write files
    df = (pd.read_excel(input_file, sheet_name=core_script_sheet_name, encoding='utf-8')).astype(str)
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


def get_book_chapters_list(chapter_find_string,input_language_column_index,target_language_column_index,df,custom_book=None):
    #Detect language
    language=detect(script_df.iloc[500,target_language_column_index])
    tmp_book_chapters_list=list()
    book_chapters_list=list()
    for s in df[(df.iloc[:, input_language_column_index].str).contains(chapter_find_string) == True].iloc[:, input_language_column_index]:
        book_list=s.split('\n')[-1]
        tmp_book_chapters_list.append(book_list)

    if custom_book is not None:
        custom_book=custom_book.upper()
        for i,b in enumerate(tmp_book_chapters_list):
            book_upper=b.upper()
            if (book_upper.__contains__(custom_book)):
                book_chapters_list.append(b)
    else:book_chapters_list=tmp_book_chapters_list
    return language,book_chapters_list



#Chapter detection is done using keyword CHP otherwise code FAILS
def get_chapter_verses(language,input_book_chapter,output_book_chapter,target_language_column_index,script_df):
    # Get indices of chapter text from heading to end line
    line_start_index=0
    line_end_index=0
    # input_book_chapter = book_chapter
    book_chapter=input_book_chapter.strip()
    book=(book_chapter.split('CHP')[0]).strip()
    chapter=int(   (book_chapter.split('CHP')[-1]).strip()          )
    # input_book_chapter=(book+' '+'CHP'+' '+str(chapter)).upper()
    input_column_name=script_df.columns[input_language_column_index]
    target_column_name=script_df.columns[target_language_column_index]
    line_column_name=script_df.columns[line_column_index]
    locations = (script_df[input_column_name].str).contains(input_book_chapter) == True
    for i in range(0,len(locations)):
        if locations[i]==True:
            line_start_index=i
            break


    #Process last book separately Assumes empty string visually is read as 'nan'
    if output_book_chapter!='REVELATION CHP 23':
        locations=(script_df[input_column_name].str).contains(output_book_chapter)==True
        for i in range(0,len(locations)):
            if locations[i]==True:
                line_end_index=i-1
                break
    else:
        if language=='en':
            e=line_start_index+1
            while script_df.iloc[e,target_language_column_index]!='nan':
                e+=1
            line_end_index=e-1
        else:
            #For other languages
            if script_df.iloc[len(script_df)-1,target_language_column_index]=='nan':
                e = line_start_index + 1
                while script_df.iloc[e, target_language_column_index] != 'nan':
                    e += 1
                line_end_index = e - 1
            else:line_end_index=len(script_df)-1





    #print(input_book_chapter,output_book_chapter,line_start_index,line_end_index)



    current_verse_num=0



    #Process chapter heading separately and extract line info.
    line_num = (script_df[line_column_name][line_start_index]).split('.')[0]

    # Extract cues from input language section
    do_not_combine_boolean_flag = (script_df[input_column_name][line_start_index]).__contains__(
        combine_tag.upper())
    # IMP: assumes the timing cues are inside the || string #Detect Minute as well, used || for detection to be safe for foreign languages
    if (script_df[input_column_name][line_start_index]).__contains__('||') and (''.join(filter(str.isdigit,re.split('\|+',script_df[input_column_name][line_start_index])[1]))).isdigit():
        # postSilence = ''.join(filter(str.isdigit, re.split('\|+', script_df[input_column_name][line_start_index])[1]))
        postSilence = (re.split('\|+', script_df[input_column_name][line_start_index])[1]).split()[1]
        time_unit = str(re.split('\|+', script_df[input_column_name][line_start_index])[1][5]).upper()
        if time_unit == 'M': postSilence = int(postSilence) * 60
    else:
        postSilence = ''


    chapter_content=dict()
    chapter_content[book_chapter]=list()

    # Read each sentence (with new line) in chapter heading into new row for better aeneas separation and replace ... with ''


    chapter_verse_num=0
    # WRITING VERSE CONTENT
    for i,word in enumerate((script_df[target_column_name][line_start_index]).split('\n')):
        word=word.strip()
        word_count=len(word.split())

        #Count chapter number into words
        character_count=len([c for c in word if c.isalpha()])+len(num2words(int(chapter)))

        #print(word)

        # Print line gap silence only if cue post silence is empty and if its last word(split by new line) in the line
        if i==len((script_df[target_column_name][line_start_index]).split('\n'))-1 and postSilence=='':
            #word = word + '\n......\n......'
            write_string=[fileset, book, chapter, line_num, chapter_verse_num,word, word_count, character_count, postSilence,line_gap_silence,do_not_combine_boolean_flag]

        elif i==len((script_df[target_column_name][line_start_index]).split('\n'))-1 and postSilence!='':
            #word = word + round(float(postSilence)/0.3) * '\n......'
            write_string = [fileset, book, chapter, line_num, chapter_verse_num, word, word_count, character_count, postSilence, '',
                            do_not_combine_boolean_flag]
        else:
            write_string = [fileset, book, chapter, line_num, chapter_verse_num, word, word_count, character_count, '',
                            '', do_not_combine_boolean_flag]

        if language == 'en':write_string = [str(i).encode("ascii", errors="ignore").decode() for i in write_string]
        else:
            # write_string = [remove_accents(str(z).lower()) for z in write_string]
            write_string = [remove_accents(str(z)) for z in write_string]
            #write_string = [str(z).encode("ascii", errors="ignore").decode() for z in write_string]

            write_string = [re.sub("⁰|¹|²|³|⁴|⁵|⁶|⁷|⁸|⁹", "", z) for z in write_string]
            #write_string = [str(i) for i in write_string]


        if word.strip()!='':  write_file.writerow(write_string)

    # For each line in chapter process and print the same info. as above
    for index in range1(line_start_index+1,line_end_index):


        # Extract line info.
        line_num=(script_df[line_column_name][index]).split('.')[0]

        #Extract cues from input language section
        do_not_combine_boolean_flag = (script_df[input_column_name][index]).__contains__(
            combine_tag.upper())
        # IMP: assumes the timing cues are inside the || string
        if (script_df[input_column_name][index]).__contains__('||') and str(re.split('\|+',script_df[input_column_name][index])[1][3]).isdigit()   and  (''.join(filter(str.isdigit,re.split('\|+',script_df[input_column_name][index])[1]))).isdigit():
            # postSilence=''.join(filter(str.isdigit,re.split('\|+',script_df[input_column_name][index])[1]))
            postSilence =(re.split('\|+', script_df[input_column_name][index])[1]).split()[1]
            # print(line_num,re.split('\|+',script_df[input_column_name][index])[1])
            time_unit = str(re.split('\|+',script_df[input_column_name][index])[1][5]).upper()
            if time_unit == 'M': postSilence = int(postSilence) * 60
        else:
            postSilence = ''


        #Extract info. from target language section

        line_content=(script_df[target_column_name][index]).split()
        verse_num_list=list()
        verse_ind_list=list()
        verse_list_dict=dict()

        #Assuming a verse is more than one word and verse num <=119 (psalms longest in bible) and check if numbering flows with verses order
        #Change this to NEW testament longest chapter
        #Made sure that the word does not contain 12,000 or a number like that
        for i,check_word in enumerate(line_content):
            #Get verse numbers
            #Give verse begin , vend
            if re.search('{(.*)}', check_word) is not None:

                if (re.search('{(.*)}', check_word).group(1)).__contains__('}') or int((re.search('{(.*)}',check_word).group(1)).split(verses_split_string)[0])<=119:

                    if (re.search('{(.*)}', check_word).group(1)).__contains__('}'):
                        content=re.search('{(.*)}', check_word).group(1)


                        # print(content.split('{')[-1])


                        verse_num_list.append(content.split('{')[-1])
                        verse_ind_list.append(i)
                        current_verse_num=content.split('{')[-1]
                        if chapter == 1 and current_verse_num==40: print('1',current_verse_num)

                    else:
                        # print((re.search('{(.*)}', check_word).group(1)))
                        verse_num_list.append((re.search('{(.*)}', check_word).group(1)))
                        verse_ind_list.append(i)
                        current_verse_num=(re.search('{(.*)}', check_word).group(1))
                        if chapter == 1 and current_verse_num==40: print('2', current_verse_num)

            elif i==0:
                if chapter == 1 and current_verse_num==40: print('4', current_verse_num)
                verse_num_list.append(current_verse_num)

                # Append verse content
                if current_verse_num not in verse_list_dict: verse_list_dict[current_verse_num] = list()
                verse_list_dict[current_verse_num].append(check_word)
                # print(line_num,verse_content,verse_num_list)
            else:
                # Append verse content
                if current_verse_num not in verse_list_dict: verse_list_dict[current_verse_num] = list()
                verse_list_dict[current_verse_num].append(check_word)
                # print(line_num,verse_content,verse_num_list)




        #WRITING VERSE CONTENT
        for i,v in enumerate(verse_list_dict):
            verse_list_dict[v]=' '.join(verse_list_dict[v])
            # verse_list_dict[v]=verse_list_dict[v]+'\n......\n......'
            word_count=len(verse_list_dict[v].split())

            alphabet_character_count = len([c for c in verse_list_dict[v] if c.isalpha()])

            # count multiple occurence of numbers into words and find the length , also add numbers without comma to the count
            num_count=0
            if re.search(r'\d+', verse_list_dict[v]) is not None:
                for u in re.findall(r'\d+,\d+',verse_list_dict[v]):
                    num_count+=len(num2words(int(u.replace(",", ""))))
                character_count = num_count+alphabet_character_count #+ len(num2words(int(re.search(r'\d+', verse_list_dict[v]).group())))
            else:
                character_count = alphabet_character_count

            if i!=0: do_not_combine_boolean_flag=''
            # Print line gap silence only if cue post silence is empty and if its last verse in the line
            if i==len(verse_list_dict)-1 and postSilence=='':

                verse_list_dict[v] = verse_list_dict[v] + '\n......\n......'

                write_string = [fileset, book, chapter, line_num, v, verse_list_dict[v], word_count, character_count,
                                postSilence,line_gap_silence,
                                do_not_combine_boolean_flag]
            elif i==len(verse_list_dict)-1 and postSilence!='':

                verse_list_dict[v] = verse_list_dict[v] + round(float(postSilence)/0.3) * '\n......'

                write_string = [fileset, book, chapter, line_num, v, verse_list_dict[v], word_count, character_count,
                                postSilence, '',
                                do_not_combine_boolean_flag]
            else:write_string = [fileset, book, chapter, line_num, v, verse_list_dict[v], word_count, character_count,
                                 '','',
                            do_not_combine_boolean_flag]
            if language == 'en':
                write_string = [str(z).encode("ascii", errors="ignore").decode() for z in write_string]
                # print(type(write_string))
                #re.sub("⁰|¹|²|³|⁴|⁵|⁶|⁷|⁸|⁹", "", write_string)

            else:
                # write_string = [remove_accents(str(z).lower()) for z in write_string]
                write_string = [remove_accents(str(z)) for z in write_string]
                #write_string = [str(z).encode("ascii", errors="ignore").decode() for z in write_string]

                write_string = [re.sub("⁰|¹|²|³|⁴|⁵|⁶|⁷|⁸|⁹", "", z) for z in write_string]

                #print(write_string)

                #write_string = [str(z) for z in write_string]
                # print(type(write_string))

                #re.sub("⁰|¹|²|³|⁴|⁵|⁶|⁷|⁸|⁹", "", write_string)

                #write_string = [str(z).encode("ascii", errors="ignore").decode() for z in write_string]

            if (verse_list_dict[v]).strip()!='': write_file.writerow(write_string)



        (chapter_content[book_chapter]).append([fileset,book,chapter,line_num, verse_list_dict, word_count,character_count,postSilence,do_not_combine_boolean_flag])




line_column_index,input_language_column_index,target_language_column_index,script_df=get_column_indexes_from_corescript()
# print(line_column_index,input_language_column_index,target_language_column_index)
#print("line_column_name:{0},input_language_column_name:{1},target_language_column_name:{2}".format(script_df.columns[line_column_index],script_df.columns[input_language_column_index],script_df.columns[target_language_column_index]))

language,complete_book_chapters_list=get_book_chapters_list(chapter_find_string,input_language_column_index,target_language_column_index,script_df)
language,book_chapters_list=get_book_chapters_list(chapter_find_string,input_language_column_index,target_language_column_index,script_df,book)

'''
print(complete_book_chapters_list)
print(book_chapters_list)
print(language)
'''

last_chapter_index=[i+1 for i, x in enumerate(complete_book_chapters_list) if x==book_chapters_list[len(book_chapters_list)-1]][0]

# import unicodedata
# myfoo = u'àà'
# unicodedata.normalize('NFD', myfoo).encode('ascii', 'ignore')

import sys
if sys.version_info.major == 3:
    unicode = str

def remove_accents(string):
    if type(string) is not unicode:
        string = unicode(string, encoding='utf-8')

    string = re.sub(u"[Äàáâãäå]", 'a', string)
    string = re.sub(u"[èéêë]", 'e', string)
    string = re.sub(u"[ìíîïɨ]", 'i', string)
    string = re.sub(u"[òóôõö]", 'o', string)
    string = re.sub(u"[ùúûü]", 'u', string)
    string = re.sub(u"[ýÿ]", 'y', string)
    string = re.sub(u"[¿]", '', string)

    return string


for i,book in enumerate(book_chapters_list):
    #print(book)
    if i != len(book_chapters_list) - 1:
        get_chapter_verses(language, book, book_chapters_list[i + 1], target_language_column_index, script_df)
    else:
        if book is None:
            get_chapter_verses(language, book, 'REVELATION CHP 23', target_language_column_index, script_df)
        else:
            #get_chapter_verses(language, book, 'REVELATION CHP 23', target_language_column_index, script_df)
            get_chapter_verses(language, book, complete_book_chapters_list[last_chapter_index], target_language_column_index, script_df)
write_file_handle.close()
