import glob,os

for each_lang in glob.glob('/Users/spanta/Desktop/pass_qc/*'):
    batch_run_string='python3 /Users/spanta/Desktop/adapted_for_batch/aeneas_test/aeneas_scripts/BibleFileTimestamps_Insert_aeneas.py -aeneas_timing_dir '+each_lang+' -aeneas_timing_err 4'
    os.system(batch_run_string)