# BibleFileTimestamps_Insert.py
#
# This program loads timings data into the bible_file_timestamps table.
# It iterates over a series of files in a directory, or over all timings directories in a tree.
#
# Usage: python3 py/BibleFileTimestamps_Insert.py  /top/dir/root/Eng  timing_est_err
# Where the 'Eng' selects all bible directories that start with 'Eng'
# Usage: python3 py/BibleFileTimestamps_Insert.py  /top/dir/root/English KJV  timing_est_err
# Where the 'English' and 'KJV' are part of one string 'Eng KJV'
# Note: the use of wildcard * is NOT expected.
# Usage: python3 py/BibleFileTimestamps_Insert_aeneas -aeneas_timing_dir /path_to/timings_dir -aeneas_timing_err 4
#Expects the last field in the aeneas_timing_dir path to have filesetid to push the timings to DB
# Sample Quality codes:
# 0 = verified by known native speaker
# 1 = verified by unknown native speaker
# 2 = verified by non-native speaker
# 3 = verified by non-speaker (eg members of the text team at FCBH who do this type of thing for a living)
# 4 = automated aeneas timings quality controlled by qinfo line timings
# 5 = automated spot-checked by non-native speaker (this is the case of most of the SAB appDef timings)
# 9 = automated unverified (probably would never put these into the DB, but if I did at least I’d have this indicator of non-confidence)


import sys
import os
import io
import re
from SQLUtility import *

#For parsing args
import argparse,glob

# TODO: change to use Config
TIM_HOST = "localhost"
TIM_USER = "sa"
TIM_PORT = 3310
TIM_DB_NAME = ""


parser = argparse.ArgumentParser(
	description='This function creates lines.csv file from core script .xls file')
aeneas_optional_arguments = parser.add_argument_group('aeneas optional arguments')
aeneas_optional_arguments.add_argument(
	'-aeneas_timing_dir', nargs=1, type=str, help='Directory containing timing files')
aeneas_optional_arguments.add_argument(
	'-aeneas_timing_err', nargs=1, type=int, help='Timing files Quality code, '
														  '0 = verified by known native speaker'
														  '1 = verified by unknown native speaker'
														  '2 = verified by non-native speaker'
														  '3 = verified by non-speaker (eg members of the text team at FCBH who do this type of thing for a living)'
														  '4 = automated aeneas timings quality controlled by qinfo line timings'
														  '5 = automated spot-checked by non-native speaker (this is the case of most of the SAB appDef timings)'
														  '9 = automated unverified (probably would never put these into the DB, but if I did at least I’d have this indicator of non-confidence)'
															)

args = parser.parse_args()
aeneas_timing_dir = args.aeneas_timing_dir[0]
aeneas_timing_err = args.aeneas_timing_err[0]

os.system('export MYSQL_PASSWD=pS193DNhaGxoO5v')


class BibleFileTimestamps_Insert():

	def __init__(self):
		self.db = SQLUtility(TIM_HOST, TIM_PORT, TIM_USER, TIM_DB_NAME)
		self.filesetRegex = re.compile(r"([A-Z1-2]+)\.mp3")
		self.xmlRegex = re.compile(r"<filename src.*>(.*)</filename>")
		self.filenameRegex = re.compile(r"[A-Z0-9]+-[0-9]+-([A-Z1-4]+)-([0-9]+)-timing.txt")
		self.timingRegex = re.compile(r"([0-9\.]+)\t([0-9\.]+)\t([0-9]+)([a-z]?)")
		self.aeneas_timing_dir=aeneas_timing_dir
		self.aeneas_timing_err=aeneas_timing_err




	def getFileId(self, filesetId, bookId, chapter):
		sql = ("SELECT bf.id FROM bible_files bf, bible_filesets bs"
			" WHERE bf.hash_id =  bs.hash_id"
			" AND bs.id = %s"
			" AND bf.book_id = %s"
			" AND bf.chapter_start = %s"
			" AND bf.verse_start = 1")
		return self.db.selectScalar(sql, (filesetId, bookId, int(chapter)))
		# This codes does not work for SNMNVSP1DA, because it has verse_start other than 1
		# Others might have this in the future.
		# Possibly we need a query that returns verse_start or verse_start and verse_end


	def getHashId(self, filesetId):
		sql = ("SELECT hash_id FROM bible_filesets WHERE asset_id = 'dbp-prod'"
			" AND set_type_code IN ('audio', 'audio_drama')"
			" AND id = %s")
		return self.db.selectScalar(sql, (filesetId))


	def processBible(self):
		filesetId =(str(self.aeneas_timing_dir)).split('/')[-1]
		values = []
		for file in sorted(glob.glob(   self.aeneas_timing_dir+'/*.txt'   )):
			file=file.split('/')[-1]
			print(file)
			if not file.startswith("."):
				result = self.filenameRegex.match(file)
				if result != None:
					book = result.group(1)
					chapter = result.group(2)
					fileId = self.getFileId(filesetId, book, chapter)
					print(fileId)
					if fileId != None:
						timing_filename = os.path.join(self.aeneas_timing_dir,file)
						timings = io.open(timing_filename, mode="r")
						priorVerse = 0
						for line in timings:
							result = self.timingRegex.search(line)
							if result != None:
								# set precision to milliseconds to match SAB timing files
								# TODO: change database schema for timing from double(8,2) to float
								timing = round(float(result.group(1)), 3)
								verseStart = int(result.group(3))
								versePart = result.group(4)
								if verseStart == 1:
									# verse 0 is used to indicate the start of the chapter introduction,
									# so AudioHLS.py appropriately creates a segment 0
									if timing == 0:
										print("WARNING: file \"%s\" missed the intro (v1 starts at 0)" % (timing_filename))
									else:
										# append a verse 0 for the intro
										values.append((fileId, 0, None, 0))
								if versePart == "" or versePart == "a":
									values.append((fileId, verseStart, None, timing))
									# check that all verses are included
									if (priorVerse + 1) != verseStart:
										print("WARNING: %s %s:%s skipped from %d to %d" % (filesetId, book, chapter, priorVerse, verseStart))
									priorVerse = verseStart
							# TODO: add an else to verify matching book and chapter in file header
					else:
						print("ERROR: No file for %s %s:%s" % (filesetId, book, chapter))
				else:
					raise Exception("Unable to parse file %s" % (file))

		#for value in values:
		#	print(value)
		deleteStmt = ("DELETE FROM bible_file_timestamps WHERE bible_file_id IN"
			" (SELECT bf.id FROM bible_files bf, bible_filesets bs"
			" WHERE bf.hash_id = bs.hash_id AND bs.id = %s)")
		errorStmt = ("REPLACE INTO bible_fileset_tags (hash_id, name, description, admin_only, iso, language_id)"
			" VALUES (%s, 'timing_est_err', %s, 0, 'eng', 6414)")
		insertStmt = "INSERT INTO bible_file_timestamps (bible_file_id, verse_start, verse_end, `timestamp`) VALUES (%s, %s, %s, %s)"
		print("%s\n", insertStmt)
		#print("%d rows to be inserted for %s, %s" % (len(values), bibleDir, filesetId))

		cursor = self.db.conn.cursor()

		try:
			sql = deleteStmt
			cursor.execute(sql, (filesetId,))
			print(sql)

			hashId = self.getHashId(filesetId)
			print(hashId)

			sql = errorStmt
			cursor.execute(sql, (hashId, self.aeneas_timing_err))
			print(sql)


			sql = insertStmt
			cursor.executemany(sql, values)
			print(sql)

			self.db.conn.commit()
			cursor.close()
		except Exception as err:
			self.db.error(cursor, sql, err)


	def process(self):
		self.processBible()
		self.db.close()


if (args.aeneas_timing_dir and args.aeneas_timing_err) is not None:
	# Perform checks to verify timing format
	chapter_count=len(glob.glob(aeneas_timing_dir+'/*.txt'))
	if chapter_count !=260:
		print('all the chapters in NT not found, #_chapters',chapter_count)
	else:
		ins = BibleFileTimestamps_Insert()
		ins.process()



