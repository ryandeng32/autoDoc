import os
import sys
from auto_doc import AutoDoc
from collections import defaultdict 

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
    for i in obj.error_pairs: 
        overview_dict[i] += len(obj.error_pairs[i])

output = [] 
for error in overview_dict: 
    output.append(f"{error}: {overview_dict[error]}")
output.sort()
for i in output:
    print(i)