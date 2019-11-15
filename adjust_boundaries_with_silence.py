def adjust_boundaries_with_silence(input_file,silence_file,output_file,input_split_field='\t',silence_split_field=',',output_split_field=','):
    #This function adjusts the boundaries of input file with silence mid points
    inc=0
    new0=list()
    with open(input_file,'r') as f:
        with open(output_file,'w') as up:
            #Read input file
            for line in f:
                line=line.replace('\n','')
                adjust_boundary0=float(line.split(input_split_field)[0])
                adjust_boundary1 = float(line.split(input_split_field)[1])
                if len(line.split(input_split_field))>2: text=output_split_field+line.split(input_split_field)[2]
                else:text=''
                inc += 1

                #Read silence file
                with open(silence_file,'r') as s:
                    for silence_bounds in s:
                        silence_start=float(silence_bounds.split(silence_split_field)[0])
                        silence_end=float(silence_bounds.split(silence_split_field)[1])
                        if silence_start<=adjust_boundary1<=silence_end:
                            adjust_boundary1=(silence_start+silence_end)/2
                            break
                s.close()
                new0.append(adjust_boundary1)
                #Write to output file
                if inc==1:up.write(str(round(adjust_boundary0,3))+output_split_field+str(round(adjust_boundary1,3))+text+'\n')
                else:up.write(str(round(new0[inc-2],3))+output_split_field+str(round(adjust_boundary1,3))+text+'\n')
        up.close()
    f.close()

'''
Example run:
adjust_boundaries_with_silence('/mark1_test/N2_ESV_ESV_029_MRK_01_VOX_edited.txt','/mark1_test/silence_boundaries_use_file.txt',
                               '/mark1_test/test.txt',input_split_field=',',silence_split_field=',',output_split_field=',')

'''

