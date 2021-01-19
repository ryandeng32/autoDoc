import os
import sys
import time 
import subprocess
from auto_doc import AutoDoc
from collections import defaultdict 
from auto_helper import print_errors

debug = False
path = os.getcwd()
if "-d" in sys.argv:
    sys.argv.remove('-d') 
    print('YEEEEE')
    debug = True 
    total_time_start = time.time ()
if len(sys.argv) == 2: 
    path = sys.argv[-1]
process = subprocess.run (['pydocstyle', path], stdout=subprocess.PIPE)
process
errors = [error.strip () for error in process.stdout.decode ("utf-8").split ("\n")]
error_pairs = defaultdict (dict) 
for i in range (len (errors) // 2):
    index = i * 2
    line_list = errors[index].split(":") 
    fname = line_list[0] 
    line_number = line_list[1].split()[0] 
    error_code = errors[index+1][:4]
    if fname not in error_pairs: 
        error_pairs[fname] = defaultdict(list)
    error_pairs[fname][error_code].append(int(line_number))
for fname in error_pairs: 
    obj = AutoDoc(fname, error_pairs[fname])
    obj.execute()
overview_dict = defaultdict(int) 
for fname in error_pairs: 
    obj = AutoDoc(fname)
    obj.error_pairs = obj.generate_error_pairs()
    for i in obj.error_pairs: 
        overview_dict[i] += len(obj.error_pairs[i])
print_errors(overview_dict)

if debug:
    total_time_end = time.time () 
    print ("Total time: ", total_time_end - total_time_start, "seconds")