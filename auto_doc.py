"""Automatically fixes PEP 257 violations for documentations."""

import os
import sys 
import time 
import subprocess
from collections import defaultdict

from auto_helper import (
    print_errors, 
    extract_docstring,
    adjust_line_num,
    get_quote_type, 
    get_first_alpha_index,
    first_non_whitespace_index,
    manage_blank_lines
)


class AutoDoc (object): 
    """A class that generates and fixes PEP 257 violations for a python file.
    
    Note: functions that modifies the line numbers need to call adjust_line_num with a change log
    """

    def __init__ (self, fname, error_pairs=None): 
        """Initialize file name.

        :param fname: The file to be processed
        """
        self.fname = fname
        self.error_pairs = error_pairs
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

    def fix_D202 (self): 
        """Fixes D202: No blank lines allowed after function docstring.
        
        This operation will change the line numbers in file. 
        """ 
        contents = self.contents 
        error_lines_num = self.error_pairs["D202"] 

        if error_lines_num: 
            log = []
            def remove_blank_lines (contents, error_lines_num): 
                line_index = error_lines_num[0] - 1
                start, end, _ = extract_docstring (contents, line_index) 
                return manage_blank_lines(contents, end + 1, log, error_lines_num)
            while error_lines_num: 
                error_lines_num = remove_blank_lines (contents, error_lines_num) 
            adjust_line_num (contents, self.error_pairs, log)
            self.contents = contents

    def fix_D204 (self): 
        """Fixes D204: 1 blank line required after class docstring.
        
        This operation will change the line numbers in file. 
        """ 
        contents = self.contents 
        error_lines_num = self.error_pairs["D204"] 

        if error_lines_num: 
            log = []
            def one_blank_line (contents, error_lines_num): 
                line_index = error_lines_num[0] - 1
                start, end, _ = extract_docstring (contents, line_index) 
                return manage_blank_lines(contents, end + 1, log, error_lines_num, True)
            while error_lines_num: 
                error_lines_num = one_blank_line (contents, error_lines_num) 
            adjust_line_num (contents, self.error_pairs, log)
            self.contents = contents

    def fix_D205 (self): 
        """Fixes D205: 1 blank line required between summary line and description.

        This operation will change the line numbers in file. 
        This function now only process two cases:
        - First line that contains alpha characters ends with period 
        - The next line starts with a capital letter that's not True or False 
        """ 
        contents = self.contents 
        error_lines_num = self.error_pairs["D205"] 
        if error_lines_num:
            log = [] 
            def add_blank_line (contents, error_lines_num): 
                canFix = False 
                line_index = error_lines_num[0] - 1
                start, end, _ = extract_docstring (contents, line_index) 
                quote_type = get_quote_type (contents[start])
                # case 1: first line ends with period 
                first_alpha_index = get_first_alpha_index (contents, start)
                line = contents[first_alpha_index] 
                if line.rstrip ()[-1] == ".": 
                    canFix = True 
                # case: the next line starts with a capital letter that's not True or False 
                next_index = first_alpha_index + 1 
                next_line = contents[next_index].strip()
                exceptions = ["True", "False"] 
                if (next_index > end or next_line == "" or next_line == quote_type or 
                    (next_line[0].isupper () and next_line.split ()[0][:4] not in exceptions)): 
                    canFix = True 
                if canFix: 
                    return manage_blank_lines (contents, next_index, log, error_lines_num, True)
                return error_lines_num[1:]
            while error_lines_num: 
                error_lines_num = add_blank_line (contents, error_lines_num) 
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

    def fix_D300 (self):
        """Fixes D300: Use triple double quotes for docstrings.
        
        This operation will NOT change the line numbers in file. 
        """ 
        contents = self.contents 
        error_lines_num = self.error_pairs["D300"]
        if error_lines_num:
            def to_triple_double_quotes (contents, line_index): 
                start, end, _ = extract_docstring (contents, line_index)
                quote_type = get_quote_type (contents[start]) 
                contents[start] = contents[start].replace (quote_type, '"""') 
                if end != start: 
                    contents[end] = contents[end].replace (quote_type, '"""') 
            for line_num in error_lines_num:
                to_triple_double_quotes (contents, line_num-1)
            self.contents = contents 

    def fix_D301 (self):
        """Fixes D301: Add r before triple double quotes if any backslashes in a docstring. 
        
        This operation will NOT change the line numbers in file. 
        """ 
        contents = self.contents 
        error_lines_num = self.error_pairs["D301"]
        if error_lines_num:
            def make_raw_docs (contents, line_index): 
                line = contents[line_index]
                index = first_non_whitespace_index(line)
                contents[line_index] = line[:index] + "r" + line[index:]
            for line_num in error_lines_num:
                make_raw_docs (contents, line_num-1)
            self.contents = contents 

    def fix_D400 (self): 
        """Fixes D400: First line should end with a period.
        
        This operation will NOT change the line numbers in file. 
        This function now only process three cases:
        - One-line docstring
        - First line that contains alpha characters ends with period 
        - The next line starts with a capital letter that's not True or False         
        """ 
        contents = self.contents 
        error_lines_num = self.error_pairs["D400"] 
        if error_lines_num:
            def add_period (contents, line_index): 
                start, end, _ = extract_docstring (contents, line_index) 
                first_line = contents[start] 
                quote_type = get_quote_type (first_line)
                quote_len = len (quote_type) 
                # case 1: one-line docstring
                if end - start == 0: 
                    content_start = first_line.find (quote_type) + quote_len
                    content_end = first_line.rfind (quote_type)
                    contents[start] = (first_line[:content_start] + first_line[content_start:content_end].strip () + 
                                       "." + first_line[content_end:])
                else: 
                    # case 2: the second line starts with a capital letter
                    first_alpha_index = get_first_alpha_index (contents, start)
                    line = contents[first_alpha_index] 
                    if line.rstrip ()[-1] == ".": 
                        contents[first_alpha_index] = line.rstrip () + "\n"
                        return
                    next_index = first_alpha_index + 1 
                    next_line = contents[next_index].strip()
                    exceptions = ["True", "False"] 
                    if (next_index > end or next_line == "" or next_line == quote_type or 
                        (next_line[0].isupper () and next_line.split ()[0][:4] not in exceptions)): 
                        if first_alpha_index == end: 
                            content_end = line.rfind (quote_type)
                            content_start = first_non_whitespace_index (line) 
                            contents[first_alpha_index] = (line[:content_start] + 
                                                           line[content_start: content_end].strip () + 
                                                           "." + line[content_end:])
                        else: 
                            contents[first_alpha_index] = line[:-1] + ".\n"
            for line_num in error_lines_num:
                add_period (contents, line_num-1)
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

    def fix_D412 (self): 
        """Fixes D412: No blank lines allowed between a section header and its content
        In the case that its section header is 'Parameters' which indicates a different style of docstring.
        
        This operation will change the line numbers in file. 
        """ 
        contents = self.contents 
        error_lines_num = self.error_pairs["D412"] 
        if error_lines_num:
            log = [] 
            def fix_header (contents, error_lines_num):
                line_index = error_lines_num[0] - 1 
                quote_type = get_quote_type (contents[line_index])
                while contents[line_index].strip () != "Parameters:": 
                    line_index += 1 
                contents[line_index] = ""
                error_lines_num = manage_blank_lines (contents, line_index, log, error_lines_num) 
                line = contents[line_index]
                starting_index = first_non_whitespace_index(line)
                while line.strip () != "" and line.strip () != quote_type: 
                    if (" --" in line):
                        line = line.replace(" --", ":")
                        starting_index = first_non_whitespace_index(line)
                        line = line[:starting_index] + ":param " + line [starting_index:]
                    if contents[line_index][-2].isalnum() == False and starting_index >= first_non_whitespace_index(contents[line_index + 1]):
                        line = line[:-2] + "\n"
                    contents[line_index] = line
                    line_index += 1 
                    line = contents[line_index] 
                return error_lines_num
            while error_lines_num: 
                error_lines_num = fix_header (contents, error_lines_num) 
            adjust_line_num (contents, self.error_pairs, log)
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
        if self.error_pairs is None: 
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
        self.fix_D200 ()        # one-line docstrings 
        self.fix_D202 ()        # remove blank lines after docs
        self.fix_D204 ()        # one blank lines after class docs
        self.fix_D205 ()        # one blank line after summary
        self.fix_D210 ()        # trim whitespaces 
        self.fix_D300 ()        # use triple double quotes 
        self.fix_D301 ()        # use raw docs for backslashes
        self.fix_D400 ()        # add period to first line
        self.fix_D403 ()        # first word capitalization 
        self.fix_D412 ()
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
    debug = False
    if "-d" in sys.argv:
        sys.argv.remove('-d') 
        debug = True 
    if len (sys.argv) == 2 and os.path.isfile (sys.argv[-1]): 
        obj = AutoDoc (sys.argv[-1]) 
        obj.execute (debug=debug) 
    else: 
        print ("ERROR: A valid file name is required.")