import os
import sys
from auto_doc import AutoDoc
from collections import defaultdict 
from auto_helper import print_errors

path = os.getcwd()
if len(sys.argv) == 2: 
    path = sys.argv[-1]
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