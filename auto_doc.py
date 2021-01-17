"""Automatically fixes PEP 257 violations for documentations."""

import os
import sys 
import time 
import subprocess
from collections import defaultdict

from auto_helper import (
    contain_alpha, 
    print_errors, 
    extract_docstring,
    adjust_line_num,
    get_quote_type, 
    get_first_alpha_index
)


class AutoDoc (object): 
    """A class that generates and fixes PEP 257 violations for a python file.
    
    Note: functions that modifies the line numbers need to call adjust_line_num with a change log
    """

    def __init__ (self, fname): 
        """Initialize file name.

        :param fname: The file to be processed
        """
        self.fname = fname
        self.error_pairs = None
        self.contents = None
    
    def generate_error_pairs (self): 
        """Generate error pairs for file.
        
        :return: A dict from the error code to a list of line numbers that have that error
        :rtype: dict 
        """
        # run pydocstyle 
        process = subprocess.run (['pydocstyle', self.fname], stdout=subprocess.PIPE)
        process
        errors = [error.strip () for error in process.stdout.decode ("utf-8").split ("\n")]
        error_pairs = defaultdict (list) 
        for i in range (len (errors) // 2):
            index = i * 2
            # line number 
            line_num = int (errors[index].split (" ")[0][len (self.fname)+1:])
            # error code 
            error_pairs[errors[index+1][:4]].append (line_num)
        return error_pairs

    def fix_D200 (self):
        """Fixes D200: One-line docstring should fit on one line with quotes.
        
        This operation will change the line numbers in file. 
        """ 
        contents = self.contents 
        error_lines_num = self.error_pairs["D200"] 

        if error_lines_num: 
            log = []
            def make_single_line (contents, error_lines_num): 
                line_index = error_lines_num[0] - 1
                quote_type = get_quote_type (contents[line_index]) 
                start, end, raw_docs = extract_docstring (contents, line_index) 
                quote_len = len (quote_type) 
                content_start = raw_docs.find (quote_type) + quote_len
                content_end = raw_docs.rfind (quote_type) 
                result_docs = (raw_docs[:content_start] + raw_docs.strip ()[quote_len:-quote_len].strip () + 
                               raw_docs[content_end:]) 
                # remove original docstring and insert new docstring
                contents[start:end+1] = [result_docs]
                log.append ((start, end - start)) 
                error_lines_num.pop (0)
                return [x - (end - start) for x in error_lines_num]
            while error_lines_num: 
                error_lines_num = make_single_line (contents, error_lines_num) 
            adjust_line_num (contents, self.error_pairs, log)
            self.contents = contents

    def fix_D210 (self): 
        """Fixes D210: No whitespaces allowed surrounding docstring text.
        
        This operation will NOT change the line numbers in file. 
        """ 
        contents = self.contents 
        error_lines_num = self.error_pairs["D210"] 
        if error_lines_num:
            def strip_whitespaces (contents, line_index):
                start, end, _ = extract_docstring (contents, line_index) 
                line = contents[start] 
                quote_type = get_quote_type (line)
                quote_len = len (quote_type) 
                content_start = line.find (quote_type) + quote_len 
                if end - start != 0: 
                    result_line = line[:content_start] + line[content_start:].strip () + "\n"
                else: 
                    content_end = line.rfind (quote_type) 
                    result_line = line[:content_start] + line[content_start:content_end].strip () + line[content_end:]
                contents[line_index] = result_line
            for line_num in error_lines_num:
                strip_whitespaces (contents, line_num-1)
            self.contents = contents 

    # # Use """triple double quotes"""
    def fix_D300 (self):
        contents = self.contents 
        error_lines_num = self.error_pairs["D300"]
        if not error_lines_num:
            return 
        def to_triple_double_quotes (contents, line_index): 
            start = line_index 
            end, quote_type, _ = extract_docstring(contents, line_index)
            contents[start] = contents[start].replace(quote_type, '"""') 
            if end != start: 
                contents[end] = contents[end].replace(quote_type, '"""') 
        for line_num in error_lines_num:
            to_triple_double_quotes (contents, line_num-1)
        self.contents = contents 
        

    # First line should end with a period
    # does NOT change ine numbers
    # best to be called after: fix_D200
    
    # handle case for trailing spaces 
    def fix_D400(self): 
        contents = self.contents 
        error_lines_num = self.error_pairs["D400"] 
        if not error_lines_num:
            return 
        # add period for specific cases 
        def add_period(contents, line_index): 
            # case 1: one-line docstring
            start = line_index 
            end, _, _ = extract_docstring(contents, line_index) 
            line = contents[line_index] 
            if end - start == 0: 
                content_end = line.rfind('"""')
                contents[line_index] = line[:content_end] + "." + line[content_end:]
            else: 
                # case 2: the second line that contains letters starts with a capital letter
                while not(contain_alpha(contents[line_index])): 
                    line_index += 1   
                first_line_num = line_index
                line_index += 1 
                if line_index > end or contents[line_index].strip() == "" or contents[line_index].strip()[0].isupper(): 
                    contents[first_line_num] = contents[first_line_num][:-1] + ".\n"
        for line_num in error_lines_num:
            add_period(contents, line_num-1)
        self.contents = contents 

    def fix_D403 (self): 
        """Fixes D403: First word of the first line should be properly capitalized.
        
        This operation will NOT change the line numbers in file. 
        """ 
        contents = self.contents 
        error_lines_num = self.error_pairs["D403"] 
        if error_lines_num:
            def capitalize_first_word (contents, line_index):
                first_alpha_index = get_first_alpha_index (contents, line_index)
                line = contents[first_alpha_index]
                for i in range (len (line)): 
                    if line[i].isalpha (): 
                        temp_list = line[i:].split (" ")
                        temp_list[0] = temp_list[0].title () 
                        break 
                contents[first_alpha_index] = line[:i] + " ".join (temp_list)

            for line_num in error_lines_num:
                capitalize_first_word (contents, line_num-1)
            self.contents = contents 

    def execute (self, debug=False): 
        """Read from and apply fixes to file.

        :param debug: Print useful info when debug is True

        Debug mode features: 
        - Print the violations before and after fixes 
        - Print out the runtime for execution
        """ 
        if debug: 
            pydocstyle_start = time.time ()
        self.error_pairs = self.generate_error_pairs ()
        if debug:
            pydocstyle_end = time.time () 

        f = open (self.fname, "r") 
        self.contents = f.readlines () 
        f.close () 
    
        if debug: 
            print_errors (self.error_pairs, "BEFORE")

        if debug: 
            fix_start = time.time ()
        # self.fix_D300 ()
        self.fix_D200 ()        # one-line docstrings 
        self.fix_D210 ()        # trim whitespaces 
        self.fix_D403 ()        # first word capitalization 
        # self.fix_D400 () 
        if debug: 
            fix_end = time.time () 

        f = open (self.fname, "w")
        f.writelines (self.contents) 
        f.close () 

        if debug: 
            self.error_pairs = self.generate_error_pairs ()
            print_errors (self.error_pairs, "AFTER") 
            print (f"pydocstyle: {pydocstyle_end - pydocstyle_start} seconds")
            print (f"Apply fixes: {fix_end - fix_start} seconds")


# for testing autoDoc with a file specified through command line arguments  
if __name__ == "__main__":
    if len (sys.argv) == 2 and os.path.isfile (sys.argv[-1]): 
        obj = AutoDoc (sys.argv[-1]) 
        obj.execute (debug=True) 
    else: 
        print ("ERROR: A valid file name is required.")