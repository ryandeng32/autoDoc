"""Apply auto_doc to python scripts inside a directory."""

import os
import sys
import time 
import subprocess
from collections import defaultdict 

from auto_doc import AutoDoc
from auto_helper import print_errors

# get error pairs (dict of dicts of list) 
def generate_error_dict(path): 
    process = subprocess.run (['pydocstyle', path], stdout=subprocess.PIPE)
    process
    errors = [error.strip () for error in process.stdout.decode ("utf-8").split ("\n")]
    error_dict = defaultdict (dict) 
    for i in range (len (errors) // 2):
        index = i * 2
        line_list = errors[index].split (":") 
        fname = line_list[0] 
        line_number = line_list[1].split ()[0] 
        error_code = errors[index+1][:4]
        if fname not in error_dict: 
            error_dict[fname] = defaultdict (list)
        error_dict[fname][error_code].append (int (line_number))
    return error_dict

debug = False
path = os.getcwd ()
if len (sys.argv) == 2: 
    path = sys.argv[-1]
elif len (sys.argv) == 3 and sys.argv[2] == "-d":
    path = sys.argv[1]
    debug = True 
if debug: 
    overview_dict = defaultdict (int) 
    error_dict = generate_error_dict (path) 
    for fname in error_dict: 
        error_pairs = error_dict[fname] 
        for i in error_pairs: 
            overview_dict[i] += len (error_pairs[i])
    print_errors (overview_dict, "BEFORE")
    total_time_start = time.time ()


# apply auto_doc to every file that has errors 
error_dict = generate_error_dict(path) 
for fname in error_dict: 
    obj = AutoDoc (fname, error_dict[fname])
    obj.execute ()
if debug:
    total_time_end = time.time () 
    print (f"Total time: {total_time_end - total_time_start} seconds\n")

    overview_dict = defaultdict (int) 
    error_dict = generate_error_dict (path) 
    for fname in error_dict: 
        error_pairs = error_dict[fname] 
        for i in error_pairs: 
            overview_dict[i] += len (error_pairs[i])
    print_errors (overview_dict, "AFTER")
