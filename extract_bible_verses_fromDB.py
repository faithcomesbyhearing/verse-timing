import pymysql,os,sys,csv

TIM_HOST = ""
TIM_USER = ""
TIM_PORT =
TIM_DB_NAME = ""



# cursor.execute(("SELECT * FROM bible_fileset_lookup"),None)
#
# result = cursor.fetchall()
# num_fields = len(cursor.description)
# field_names = [i[0] for i in cursor.description]
# print(field_names)
conn = pymysql.connect(host=TIM_HOST,user=TIM_USER,password="",db=TIM_DB_NAME,port=TIM_PORT,charset='utf8mb4',cursorclass=pymysql.cursors.Cursor)
cursor=conn.cursor()
#cursor.execute(("select * from bible_fileset_lookup where stocknumber = %s"), ("N2FLM/UBS"))
cursor.execute(("select book_id as 'book',chapter as 'chapter',verse_start as 'verse_number',verse_text as 'verse_content1' from bible_verses where hash_id=%s ORDER BY book_id,chapter,verse_start;"), ("4a1a463692a2"))
result = cursor.fetchall()
cursor.close()

filesetid='HBRHMTN2DA'
column_names = [i[0] for i in cursor.description]
os.popen('mkdir /home/ubuntu/aeneas_test/aeneas_dirs/core_scripts/'+filesetid)
os.popen('chmod a+rwx /home/ubuntu/aeneas_test/aeneas_dirs/core_scripts/'+filesetid)
fp = open('/home/ubuntu/aeneas_test/aeneas_dirs/core_scripts/'+filesetid+'/'+filesetid+'_bible_verses.csv', 'w')
myFile = csv.writer(fp, lineterminator = '\n')
myFile.writerow(column_names)   
myFile.writerows(result)
fp.close()

cursor=conn.cursor()
cursor.execute(("select * from bible_fileset_lookup where stocknumber = %s"), (sys.argv[1]))
result = cursor.fetchall()
cursor.close()
for each_result in result:print(each_result)

#for each_result in result:print(each_result)
