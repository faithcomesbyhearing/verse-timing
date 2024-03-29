import argparse,re,pandas as pd,os,csv,sys
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
optional_args.add_argument('-target_pointer', nargs=1, type=str,default=['2'],help='Integer to add to input language column index to get target language in corescript. '
                                                                                 'Default: find_string column index + 2')
optional_args.add_argument('-line_pointer', nargs=1, type=str,default=['-2'],help='Integer to add to input language column index to get line number in corescript. '
                                                                                'Default: find_string column index - 2')


args = parser.parse_args()
print(args)
input_file=args.i[0]
output_file=args.o[0]
fileset=args.fileset[0]

core_script_sheet_name=args.sheetname[0]
if args.book is not None:
    book=(str(args.book[0])).lower()
else:book=None
find_string=args.find_string[0]
target_pointer=int(args.target_pointer[0])
line_num_pointer=int(args.line_pointer[0])

#custom tags
combine_tag='DO NOT COMBINE'
line_gap_silence=0.5
verses_split_string='-'
chapter_find_string='CHP'

if not os.path.isdir('/'.join(output_file.split('/')[0:-1])):
    os.mkdir('/'.join(output_file.split('/')[0:-1]))

write_file_handle=open(output_file,'w',encoding='utf-8')
write_file = csv.writer(write_file_handle)

# Write header as requested by user
if not(args.noheader):write_file.writerow(('fileset','book','chapter','line_number', 'verse_number','verse_content','words','characters','postSilence_secs_cue','expected_post_silence_secs','do_not_combine_boolean_flag'))



# Get the first column index of line numbers, input language, target language and corescript dataframe
def get_column_indexes_from_corescript(input_file=input_file,core_script_sheet_name=core_script_sheet_name,find_string=find_string,target_pointer=target_pointer):
    line_column_index=9
    input_language_column_index=11
    target_language_column_index=13
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

    try:
        # Get indices of chapter text from heading to end line
        line_start_index=0
        line_end_index=0
        # input_book_chapter = book_chapter
        book_chapter=input_book_chapter.strip()
        book=(book_chapter.split('CHP')[0]).strip()

        #print(len(book_chapter.split('CHP')))
        if len(book_chapter.split('CHP'))>1:
            chapter=int(   (book_chapter.split('CHP')[-1]).strip()          )
        else:
            chapter=1


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


        current_verse_num=0



        #Process chapter heading separately and extract line info.
        line_num = (script_df[line_column_name][line_start_index]).split('.')[0]

        # Extract cues from input language section
        do_not_combine_boolean_flag = (script_df[input_column_name][line_start_index]).__contains__(
            combine_tag.upper())
        # IMP: assumes the timing cues are inside the || string #Detect Minute as well, used || for detection to be safe for foreign languages
        if (script_df[input_column_name][line_start_index]).__contains__('|') and (''.join(filter(str.isdigit,re.split('\|+',script_df[input_column_name][line_start_index])[1]))).isdigit():
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
                write_string = [remove_accents(str(z)) for z in write_string]
                write_string = [re.sub("⁰|¹|²|³|⁴|⁵|⁶|⁷|⁸|⁹", "", z) for z in write_string]


            if word.strip()!='':  write_file.writerow(write_string)

        # For each line in chapter process and print the same info. as above
        for index in range1(line_start_index+1,line_end_index):


            # Extract line info.
            line_num=(script_df[line_column_name][index]).split('.')[0]

            #Extract cues from input language section
            do_not_combine_boolean_flag = (script_df[input_column_name][index]).__contains__(
                combine_tag.upper())
            postSilence = ''


            #Extract info. from target language section
            line_content=(script_df[target_column_name][index]).split()
            verse_num_list=list()
            verse_ind_list=list()
            verse_list_dict=dict()

            #Assuming a verse is more than one word and verse num <=119 (psalms longest in bible) and check if numbering flows with verses order
            for i,check_word in enumerate(line_content):
                #Get verse numbers
                #Give verse begin , vend
                if re.search('\[(.*)\]', check_word) is not None:

                    if (re.search('\[(.*)\]', check_word).group(1)).__contains__(']') or int((re.search('\[(.*)\]',check_word).group(1)).split(verses_split_string)[0])<=119:

                        if (re.search('\[(.*)\]', check_word).group(1)).__contains__(']'):
                            content=re.search('\[(.*)\]', check_word).group(1)

                            verse_num_list.append(content.split('[')[-1])
                            verse_ind_list.append(i)
                            current_verse_num=content.split('[')[-1]
                            if chapter == 1 and current_verse_num==40: print('1',current_verse_num)

                        else:
                            verse_num_list.append((re.search('\[(.*)\]', check_word).group(1)))
                            verse_ind_list.append(i)
                            current_verse_num=(re.search('\[(.*)\]', check_word).group(1))
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


                else:
                    write_string = [remove_accents(str(z)) for z in write_string]
                    write_string = [re.sub("⁰|¹|²|³|⁴|⁵|⁶|⁷|⁸|⁹", "", z) for z in write_string]

                if (verse_list_dict[v]).strip()!='': write_file.writerow(write_string)

            (chapter_content[book_chapter]).append([fileset,book,chapter,line_num, verse_list_dict, word_count,character_count,postSilence,do_not_combine_boolean_flag])
    except Exception as err:
        print(
            type(e).__name__,  # TypeError
            __file__,  # /tmp/example.py
            e.__traceback__.tb_lineno  # 2
        )

line_column_index,input_language_column_index,target_language_column_index,script_df=get_column_indexes_from_corescript()
print(line_column_index,input_language_column_index,target_language_column_index)

language,complete_book_chapters_list=get_book_chapters_list(chapter_find_string,input_language_column_index,target_language_column_index,script_df)
language,book_chapters_list=get_book_chapters_list(chapter_find_string,input_language_column_index,target_language_column_index,script_df,book)
last_chapter_index=[i+1 for i, x in enumerate(complete_book_chapters_list) if x==book_chapters_list[len(book_chapters_list)-1]][0]


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


book_chapters_list=['MATTHEW CHP  1', 'MATTHEW CHP 2', 'MATTHEW CHP 3', 'MATTHEW CHP 4', 'MATTHEW CHP 5', 'MATTHEW CHP 6', 'MATTHEW CHP 7', 'MATTHEW CHP 8', 'MATTHEW CHP 9', 'MATTHEW CHP 10', 'MATTHEW CHP 11', 'MATTHEW CHP 12', 'MATTHEW CHP 13', 'MATTHEW CHP 14', 'MATTHEW CHP 15', 'MATTHEW CHP 16', 'MATTHEW CHP 17', 'MATTHEW CHP 18', 'MATTHEW CHP 19', 'MATTHEW CHP 20', 'MATTHEW CHP 21', 'MATTHEW CHP 22', 'MATTHEW CHP 23', 'MATTHEW CHP 24', 'MATTHEW CHP 25', 'MATTHEW CHP 26', 'MATTHEW CHP 27', 'MATTHEW CHP 28', 'MARK CHP 1', 'MARK CHP 2', 'MARK CHP 3', 'MARK CHP 4', 'MARK CHP 5', 'MARK CHP 6', 'MARK CHP 7', 'MARK CHP 8', 'MARK CHP 9', 'MARK CHP 10', 'MARK CHP 11', 'MARK CHP 12', 'MARK CHP 13', 'MARK CHP 14', 'MARK CHP 15', 'MARK CHP 16', 'LUKE CHP 1', 'LUKE CHP 2', 'LUKE CHP 3', 'LUKE CHP 4', 'LUKE CHP 5', 'LUKE CHP 6', 'LUKE CHP 7', 'LUKE CHP 8', 'LUKE CHP 9', 'LUKE CHP 10', 'LUKE CHP 11', 'LUKE CHP 12', 'LUKE CHP 13', 'LUKE CHP 14', 'LUKE CHP 15', 'LUKE CHP 16', 'LUKE CHP 17', 'LUKE CHP 18', 'LUKE CHP 19', 'LUKE CHP 20', 'LUKE CHP 21', 'LUKE CHP 22', 'LUKE CHP 23', 'LUKE CHP 24', 'JOHN CHP 1', 'JOHN CHP 2', 'JOHN CHP 3', 'JOHN CHP 4', 'JOHN CHP 5', 'JOHN CHP 6', 'JOHN CHP 7', 'JOHN CHP 8', 'JOHN CHP 9', 'JOHN CHP 10', 'JOHN CHP 11', 'JOHN CHP 12', 'JOHN CHP 13', 'JOHN CHP 14', 'JOHN CHP 15', 'JOHN CHP 16', 'JOHN CHP 17', 'JOHN CHP 18', 'JOHN CHP 19', 'JOHN CHP 20', 'JOHN CHP 21', 'ACTS CHP 1', 'ACTS CHP 2', 'ACTS CHP 3', 'ACTS CHP 4', 'ACTS CHP 5', 'ACTS CHP 6', 'ACTS CHP 7', 'ACTS CHP 8', 'ACTS CHP 9', 'ACTS CHP 10', 'ACTS CHP 11', 'ACTS CHP 12', 'ACTS CHP 13', 'ACTS CHP 14', 'ACTS CHP 15', 'ACTS CHP 16', 'ACTS CHP 17', 'ACTS CHP 18', 'ACTS CHP 19', 'ACTS CHP 20', 'ACTS CHP 21', 'ACTS CHP 22', 'ACTS CHP 23', 'ACTS CHP 24', 'ACTS CHP 25', 'ACTS CHP 26', 'ACTS CHP 27', 'ACTS CHP 28', 'ROMANS CHP 1', 'ROMANS CHP 2', 'ROMANS CHP 3', 'ROMANS CHP 4', 'ROMANS CHP 5', 'ROMANS CHP 6', 'ROMANS CHP 7', 'ROMANS CHP 8', 'ROMANS CHP 9', 'ROMANS CHP 10', 'ROMANS CHP 11', 'ROMANS CHP 12', 'ROMANS CHP 13', 'ROMANS CHP 14', 'ROMANS CHP 15', 'ROMANS CHP 16', '1 CORINTHIANS CHP 1', '1 CORINTHIANS CHP 2', '1 CORINTHIANS CHP 3', '1 CORINTHIANS CHP 4', '1 CORINTHIANS CHP 5', '1 CORINTHIANS CHP 6', '1 CORINTHIANS CHP 7', '1 CORINTHIANS CHP 8', '1 CORINTHIANS CHP 9', '1 CORINTHIANS CHP 10', '1 CORINTHIANS CHP 11', '1 CORINTHIANS CHP 12', '1 CORINTHIANS CHP 13', '1 CORINTHIANS CHP 14', '1 CORINTHIANS CHP 15', '1 CORINTHIANS CHP 16', '2 CORINTHIANS CHP 1', '2 CORINTHIANS CHP 2', '2 CORINTHIANS CHP 3', '2 CORINTHIANS CHP 4', '2 CORINTHIANS CHP 5', '2 CORINTHIANS CHP 6', '2 CORINTHIANS CHP 7', '2 CORINTHIANS CHP 8', '2 CORINTHIANS CHP 9', '2 CORINTHIANS CHP 10', '2 CORINTHIANS CHP 11', '2 CORINTHIANS CHP 12', '2 CORINTHIANS CHP 13', 'GALATIANS CHP 1', 'GALATIANS CHP 2', 'GALATIANS CHP 3', 'GALATIANS CHP 4', 'GALATIANS CHP 5', 'GALATIANS CHP 6', 'EPHESIANS CHP 1', 'EPHESIANS CHP 2', 'EPHESIANS CHP 3', 'EPHESIANS CHP 4', 'EPHESIANS CHP 5', 'EPHESIANS CHP 6', 'PHILIPPIANS CHP 1', 'PHILIPPIANS CHP 2', 'PHILIPPIANS CHP 3', 'PHILIPPIANS CHP 4', 'COLOSSIANS CHP 1', 'COLOSSIANS CHP 2', 'COLOSSIANS CHP 3', 'COLOSSIANS CHP 4', '1 THESSALONIANS CHP 1', '1 THESSALONIANS CHP 2', '1 THESSALONIANS CHP 3', '1 THESSALONIANS CHP 4', '1 THESSALONIANS CHP 5', '2 THESSALONIANS CHP 1', '2 THESSALONIANS CHP 2', '2 THESSALONIANS CHP 3', '1 TIMOTHY CHP 1', '1 TIMOTHY CHP 2', '1 TIMOTHY CHP 3', '1 TIMOTHY CHP 4', '1 TIMOTHY CHP 5', '1 TIMOTHY CHP 6', '2 TIMOTHY CHP 1', '2 TIMOTHY CHP 2', '2 TIMOTHY CHP 3', '2 TIMOTHY CHP 4', 'TITUS CHP 1', 'TITUS CHP 2', 'TITUS CHP 3', 'PHILEMON', 'HEBREWS CHP 1', 'HEBREWS CHP 2', 'HEBREWS CHP 3', 'HEBREWS CHP 4', 'HEBREWS CHP 5', 'HEBREWS CHP 6', 'HEBREWS CHP 7', 'HEBREWS CHP 8', 'HEBREWS CHP 9', 'HEBREWS CHP 10', 'HEBREWS CHP 11', 'HEBREWS CHP 12', 'HEBREWS CHP 13', 'JAMES CHP 1', 'JAMES CHP 2', 'JAMES CHP 3', 'JAMES CHP 4', 'JAMES CHP 5', '1 PETER CHP 1', '1 PETER CHP 2', '1 PETER CHP 3', '1 PETER CHP 4', '1 PETER CHP 5', '2 PETER CHP 1', '2 PETER CHP 2', '2 PETER CHP 3', '1 JOHN CHP 1', '1 JOHN CHP 2', '1 JOHN CHP 3', '1 JOHN CHP 4', '1 JOHN CHP 5', '2 JOHN', '3 JOHN', 'JUDE', 'REVELATION CHP 1', 'REVELATION CHP 2', 'REVELATION CHP 3', 'REVELATION CHP 4', 'REVELATION CHP 5', 'REVELATION CHP 6', 'REVELATION CHP 7', 'REVELATION CHP 8', 'REVELATION CHP 9', 'REVELATION CHP 10', 'REVELATION CHP 11', 'REVELATION CHP 12', 'REVELATION CHP 13', 'REVELATION CHP 14', 'REVELATION CHP 15', 'REVELATION CHP 16', 'REVELATION CHP 17', 'REVELATION CHP 18', 'REVELATION CHP 19', 'REVELATION CHP 20', 'REVELATION CHP 21', 'REVELATION CHP 22']


for i,book in enumerate(book_chapters_list):
    if i != len(book_chapters_list) - 1:
        get_chapter_verses(language, book, book_chapters_list[i + 1], target_language_column_index, script_df)
    else:
        if book is None:
            get_chapter_verses(language, book, 'REVELATION CHP 23', target_language_column_index, script_df)
        else:
            get_chapter_verses(language, book.strip(), 'REVELATION CHP 23', target_language_column_index, script_df)
write_file_handle.close()
