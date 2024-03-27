from collections import OrderedDict
import xlsxwriter,pandas as pd
from collections import Counter
import textdistance

df=pd.read_csv('/Users/spanta/Downloads/FCBH_QC_MMS/N2_Tugutil/output_QC_eng.csv',encoding='utf-8',index_col=None,dtype=str)
tmp_df=pd.read_csv('/Users/spanta/Downloads/FCBH_QC_MMS/N2_Tugutil/output_QC_eng.csv',encoding='utf-8',index_col=None,dtype=str)

writer = pd.ExcelWriter('/Users/spanta/Downloads/FCBH_QC_MMS/N2_Tugutil/analyzed.xlsx', engine='xlsxwriter')
tmp_df.to_excel(writer, sheet_name='Sheet1', header=False,index=False)
workbook  = writer.book
worksheet = writer.sheets['Sheet1']
cell_format_red = workbook.add_format({'font_color': 'red'})
cell_format_default = workbook.add_format({'bold': False})


'''
get the logic where combine two words to form a word and if edit dist is <3 then pass on updating ind
play with the logic because osiki is different from nosiki so choose a right phonetic thing to differentiate and not lose this with edit distance
'''

for each_row in range(df.shape[0]):
    comment=''
    target_text=str(df['transcribed_text'][each_row]).split(' ')
    source_text = str(df['source_text'][each_row]).split(' ')

    if int(df['difference'][each_row])>=20:
        comment='Missing audio around highlighted word: '
    else:
        comment='Check text around highlighted word: '

    for each_column in range(df.shape[1]):
        if each_column!=4 :
            worksheet.write(each_row,each_column,df.iloc[each_row,each_column])
        else:

            target_ind = 0
            source_ind = 0
            difference_flag = 0
            clubbed_words = 0

            if len(source_text) >= len(target_text):
                #print('s>=t',df['line_number'][each_row])

                while target_ind < len(target_text):
                    if int(df['line_number'][each_row]) == 1854:print('begin loop',df['line_number'][each_row],target_ind,'len(target_text)->',len(target_text),source_ind,'len(source_text)->',len(source_text),target_text[target_ind],source_text[source_ind])
                    if source_text[source_ind] != target_text[target_ind] and textdistance.mra.distance(target_text[target_ind],source_text[source_ind])>0:# and textdistance.levenshtein.distance(target_text[target_ind],source_text[source_ind])>1: #abs(len(source_text[source_ind])-len(target_text[target_ind]))>1:
                        if source_ind<len(source_text)-1 and target_ind<len(target_text)-1 and (target_text[target_ind] + target_text[target_ind + 1] == source_text[source_ind] or target_text[target_ind] + '-'+target_text[target_ind + 1] == source_text[source_ind]):# and abs( len(target_text[target_ind] + target_text[target_ind + 1])-len(source_text[source_ind]))<2:
                            target_ind+=2
                            source_ind += 1
                            clubbed_words+=1
                        elif source_ind<len(source_text)-1 and (source_text[source_ind] + source_text[source_ind + 1] == target_text[target_ind] or source_text[source_ind] + '-'+source_text[source_ind + 1] == target_text[target_ind]):# and abs( len(source_text[source_ind] + source_text[source_ind + 1])-len(target_text[target_ind]))<2:
                                clubbed_words += 1
                                if source_ind!=len(source_text)-2:
                                    source_ind+=2
                                    target_ind += 1
                                else:
                                    break
                        else:
                            #print('we are here')
                            difference_flag =1
                            break
                    else:
                        target_ind+=1
                        source_ind+=1

                if int(df['line_number'][each_row]) == 1854:print('end of loop',df['line_number'][each_row],target_ind,'len(target_text)->',len(target_text),source_ind,'len(source_text)->',len(source_text),difference_flag)
                '''
                for each_target_word in target_text:
                    # print(df['line_number'][each_row],'---------')
                    if target_ind <= len(target_text) - 2 and target_text[target_ind] + target_text[target_ind + 1] == \
                            source_text[source_ind]:
                        target_ind += 2
                        source_ind += 1
                        clubbed_words += 1
                        pass
                    # print('here3.5',target_ind,source_ind,len(target_text),len(source_text))

                    if target_text[target_ind] != source_text[source_ind]:
                        # print('here4',target_ind,source_ind,target_text[target_ind], source_text[source_ind])
                        difference_flag = 1
                        # print(difference_flag)
                        break

                    target_ind += 1
                    source_ind += 1
                    # print(ind)
                    if difference_flag == 1:
                        break
                target_ind -= 1
                source_ind -= -1
                # print('here5', target_ind, source_ind)
                # target_text[target_ind], source_text[source_ind])
                # print('final',target_ind,target_text[target_ind],source_ind, difference_flag)

                difference_words = list((Counter(source_text) - Counter(target_text)).elements())
                '''
            # difference_words=list((Counter(target_text) - Counter(source_text)).elements())
            # print(len(difference_words),difference_flag,ind)
            # index_list=list()
            # for each_word in difference_words:
            #     index_list.append(target_text.index(each_word))

            # print(df['line_number'][each_row], df['difference'][each_row])
            # print(ind)

            # if int(df['line_number'][each_row]) == 2589:
            #     print(df['line_number'][each_row], df['difference'][each_row])
            #     print(target_text)
            #     print(source_text)
            #     print(difference_words)
            #     print(ind)

            # print(df['line_number'][each_row], 'here0')
            #
            # print(df['line_number'][each_row], df['difference'][each_row])
            #
            # print('len target', len(target_text), target_text)
            #
            # print('len source', len(source_text), source_text)
            #
            # # print(difference_words,len(difference_words))

            #print(difference_flag)


                if int(df['difference'][each_row]) != 0 and difference_flag==1:
                    # print(df['line_number'][each_row],'here1')
                    #
                    # print(df['line_number'][each_row], df['difference'][each_row])
                    #
                    # print('len target', len(target_text),target_text)
                    #
                    # print('len source', len(source_text),source_text)

                    # print(difference_words)

                    # print(ind)

                    if len(source_text) > len(target_text)-clubbed_words and source_ind < len(source_text) - 1 and difference_flag==1:
                        # print(df['line_number'][each_row], 'here2')
                        #
                        # print(df['line_number'][each_row], df['difference'][each_row])
                        #
                        # print('len target', len(target_text))
                        #
                        # print('len source', len(source_text))

                        # print(difference_words)

                        # print(target_ind)

                        if (source_ind == 0):
                            # if int(df['line_number'][each_row]) == 2589: print(df['difference'][each_row], difference_flag,
                            #                                                    df['line_number'][each_row], each_column,
                            #                                                    len(target_text), len(source_text),
                            #                                                    target_ind < len(target_text) - 1,
                            #                                                    target_text[target_ind] + target_text[
                            #                                                        target_ind + 1] != source_text[
                            #                                                        target_ind])

                            worksheet.write_rich_string(each_row, each_column, cell_format_red,comment,cell_format_red,
                                                        source_text[source_ind],
                                                        cell_format_default, ' ', cell_format_default,
                                                        ' '.join(source_text[source_ind+ 1:]))
                        if (source_ind > 0 and source_ind != len(source_text) - 1):
                            worksheet.write_rich_string(each_row, each_column, cell_format_red,comment,cell_format_default,
                                                        ' '.join(source_text[0:source_ind]) + ' ',
                                                        cell_format_red,
                                                        source_text[source_ind+1], cell_format_default,
                                                        ' ' + ' '.join(source_text[source_ind+ 2 :]))

                        if (source_ind == len(source_text) - 1):
                            worksheet.write_rich_string(each_row, each_column, cell_format_red,comment,cell_format_default,
                                                        ' '.join(source_text[0:source_ind]) + ' ',
                                                        cell_format_red,
                                                        source_text[source_ind])
                elif len(target_text) != len(source_text)-clubbed_words:
                    comment='Highlighted words missing in audio: '
                    worksheet.write_rich_string(each_row, each_column, cell_format_red, comment, cell_format_default,
                                                ' '.join(source_text[0:len(target_text)]) +' ',
                                                cell_format_red,
                                                ' '.join(source_text[len(target_text):]))

            else:
                #print('t>s',df['line_number'][each_row])
                # if target text is > source text
                # print(df['line_number'][each_row],'here1')
                #
                # print(df['line_number'][each_row], df['difference'][each_row])
                #
                # print('len target', len(target_text),target_text)
                #
                # print('len source', len(source_text),source_text)
                #
                # print(difference_words)
                #
                # print(ind)
                # if len(difference_words)==0:
                #     index_list=list()
                difference_words = list((Counter(target_text) - Counter(source_text)).elements())
                #     for each_word in difference_words:
                #         index_list.append(source_text.index(each_word))
                target_ind =0
                source_ind =0
                clubbed_words =0
                difference_flag=0
                #print('check here',source_ind,len(source_text))
                while source_ind < len(source_text):
                    if int(df['line_number'][each_row]) == 1854:print('begin loop',df['line_number'][each_row],target_ind,'len(target_text)->',len(target_text),source_ind,'len(source_text)->',len(source_text))
                    if target_text[target_ind] != source_text[source_ind] and textdistance.mra.distance(target_text[target_ind],source_text[source_ind])>0:# and textdistance.levenshtein.distance(target_text[target_ind],source_text[source_ind])>1:#abs(len(source_text[source_ind])-len(target_text[target_ind]))>1:
                        if target_ind<len(target_text)-1 and (target_text[target_ind] + target_text[target_ind + 1] == source_text[source_ind] or target_text[target_ind] + '-'+target_text[target_ind + 1] == source_text[source_ind]):# and abs( len(target_text[target_ind] + target_text[target_ind + 1])-len(source_text[source_ind]))<2:
                            if target_ind!=len(target_text)-2:
                                target_ind+=2
                                source_ind += 1
                            else:
                                break
                        elif source_ind<len(source_text)-1 and (source_text[source_ind] + source_text[source_ind + 1] == target_text[target_ind] or source_text[source_ind] + '-'+source_text[source_ind + 1] == target_text[target_ind]):# and abs( len(source_text[source_ind] + source_text[source_ind + 1])-len(target_text[target_ind]))<2:
                                source_ind+=2
                                target_ind += 1
                        else:
                            #print('we are here')
                            difference_flag =1
                            #print('diff word->',target_text[target_ind])
                            break
                    else:
                        target_ind+=1
                        source_ind+=1
                if int(df['line_number'][each_row]) == 1854:print(df['line_number'][each_row],target_ind, len(target_text),source_ind,len(source_text),'dif flag->',difference_flag)
            '''    
            for each_target_word in target_text:
                print('beginning of loop',target_ind,source_ind)
                if target_ind==len(target_text)-1:break
                if target_ind<=len(target_text)-2 and target_text[target_ind] + target_text[target_ind + 1] == source_text[source_ind]:
                    #print('crazy target_ind',target_ind)
                    if target_ind == len(target_text) - 2:
                        break
        
                    else:
                        target_ind += 2
                        source_ind += 1
                        clubbed_words += 1
                        pass
                #print('here3.5', target_ind, source_ind)
                # , target_text[target_ind], source_text[source_ind])
        
                if target_text[target_ind] != source_text[source_ind]:
                    print('target_text[target_ind] != source_text[source_ind]',df['line_number'][each_row],target_text[target_ind],source_text[source_ind],target_ind, source_ind)
                    #print('here4', target_ind, source_ind, target_text[target_ind], source_text[source_ind])
                    difference_flag = 1
                    #print(difference_flag)
                    break
                if target_ind<len(target_text)-1:target_ind += 1
                if target_ind == len(target_text) - 2 :target_ind += 1
                if target_ind==len(target_text):
                    target_ind-=1
        
                if source_ind<=len(source_text)-1:
                    source_ind += 1
                if source_ind==len(source_text):
                    source_ind-=1
        
                # print(ind)
                if difference_flag == 1:
                    break
        
                print('End of loop', df['line_number'][each_row],target_ind, source_ind)
            '''

            if int(df['line_number'][each_row])==6165: print('final6165', target_ind, source_text[source_ind], source_ind)

            if difference_flag==1:
                if (target_ind == 0):
                    #print('goof off')
                    worksheet.write_rich_string(each_row, each_column,cell_format_red,comment, cell_format_red,
                                                target_text[target_ind ],
                                                cell_format_default, ' ', cell_format_default,
                                                ' '.join(target_text[1:]))

                if (target_ind > 0 and target_ind != len(target_text) - 1):
                    worksheet.write_rich_string(each_row, each_column, cell_format_red,comment,cell_format_default,
                                                ' '.join(target_text[0:target_ind]) + ' ',
                                                cell_format_red,
                                                target_text[target_ind],
                                                cell_format_default,
                                                ' ' + ' '.join(target_text[target_ind + 1:]))

                if (target_ind == len(target_text) - 1):
                    worksheet.write_rich_string(each_row, each_column,cell_format_red, comment,cell_format_default,
                                                ' '.join(target_text[0:target_ind]) + ' ',
                                                cell_format_red,
                                                ' '.join(target_text[target_ind:]))

workbook.close()



# data = {"1":["xyz",""],"2":["abc","def"],"3":["zzz",""]}
#
# # Use an OrderedDict to maintain the order of the columns
# data = OrderedDict((k,data.get(k)) for k in sorted(data.keys()))
#
# # Open an Excel workbook
# workbook = xlsxwriter.Workbook('dict_to_excel.xlsx')
#
# # Set up a format
# book_format = workbook.add_format(properties={'bold': True, 'font_color': 'red'})
#
# # Create a sheet
# worksheet = workbook.add_worksheet('dict_data')
#
# # Write the headers
# for col_num, header in enumerate(data.keys()):
#     worksheet.write(0,col_num, int(header))
#
# bold = workbook.add_format({'font_name':'Tahoma', 'bold': True, 'font_size':14})
# normal = workbook.add_format({'font_name':'Tahoma', 'font_size':11})
#
# # Save the data from the OrderedDict into the excel sheet
# for row_num,row_data in enumerate(zip(*data.values())):
#     for col_num, cell_data in enumerate(row_data):
#         print(row_num+1, col_num, cell_data)
#         if cell_data ==  "xyz":
#             worksheet.write(row_num+1, col_num, cell_data, book_format)
#             worksheet.write_rich_string(row_num+1, col_num,bold, 'bold', normal, 'normal')
#
#         else:
#             worksheet.write(row_num+1, col_num, cell_data)
#
# # Close the workbook
# workbook.close()