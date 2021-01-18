import os
import sys
import time 
from auto_doc import AutoDoc
from collections import defaultdict 
from auto_helper import print_errors

debug = False
path = os.getcwd()
if len(sys.argv) == 2: 
    path = sys.argv[-1]
elif len(sys.argv) == 3 and sys.argv[2] == "-d":
    path = sys.argv[1]
    debug = True 
    total_time_start = time.time ()

hidden = [".", "~"]
ignored_files = ['auto_doc.py', 'auto_overview.py'] 
all_files = [] 
for root, dirs, files in os.walk(path):
    files = [f for f in files if not f[0] == '.']
    dirs[:] = [d for d in dirs if not d[0] == '.']
    all_files.extend([root + "/" + fname for fname in files if fname not in ignored_files])
files = [f for f in all_files if os.path.splitext(f)[1] == ".py"]
overview_dict = defaultdict(int) 
for fname in files: 
    obj = AutoDoc(fname)
    obj.error_pairs = obj.generate_error_pairs()
    for i in obj.error_pairs: 
        overview_dict[i] += len(obj.error_pairs[i])

print_errors(overview_dict)
for fname in files: 
    obj = AutoDoc(fname)
    obj.execute()
overview_dict = defaultdict(int) 

for fname in files: 
    obj = AutoDoc(fname)
    obj.error_pairs = obj.generate_error_pairs()
    contents = [] 
    for i in obj.error_pairs: 
        overview_dict[i] += len(obj.error_pairs[i])
    if "D400" in obj.error_pairs: 
        contents.append({fname: obj.error_pairs["D400"]})
    f = open("errors.txt", "w")
    f.writelines("contents")
    f.close()
print_errors(overview_dict)

if debug:
    total_time_end = time.time () 
    print ("Total time: ", total_time_end - total_time_start, "seconds")