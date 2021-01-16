"""Automatically fixes PEP 257 violations for documentations."""

import os
import sys 
import subprocess
from collections import defaultdict

from auto_helper import contain_alpha, print_errors, extract_docstring, adjust_line_num


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
        
        This operation will change the content and the line numbers in file. 
        """ 
        contents = self.contents 
        error_lines_num = self.error_pairs["D200"] 
        if not error_lines_num:
            return 
        log = []
        # make one-line docstring fit on one line
        def make_single_line(contents, line_index): 
            start = line_index 
            end, quote_type, raw_docstring = extract_docstring(contents, line_index) 
            content_start = raw_docstring.find('"""')
            processed_docstring = raw_docstring[:content_start] + '"""' + raw_docstring.strip()[3:-3].strip() + '"""\n'
            # remove original docstring and insert new docstring
            for i in range(end - start + 1): 
                contents.pop(start)
            contents.insert(start, processed_docstring)
            for i in range(len(error_lines_num)): 
                error_lines_num[i] -= end - start
            log.append((start, end-start))
        # apply fix for every D200 violation in self.fname
        for i in range(len(error_lines_num)): 
            make_single_line(contents, error_lines_num[i] - 1) 
        adjust_line_num(contents, log, self.error_pairs)
        self.contents = contents

        

    # No whitespaces allowed surrounding docstring text
    # does NOT change line numbers 
    def fix_D210(self): 
        contents = self.contents 
        error_lines_num = self.error_pairs["D210"] 
        if not error_lines_num:
            return 
        # strip the whitespaces in docstring's first line
        def strip_whitespaces(contents, line_index):
            raw_line = contents[line_index] 
            start = line_index 
            end, quote_type, _ = extract_docstring(contents, line_index)
            content_start = raw_line.find(quote_type)
            if end - start != 0: 
                processed_line = raw_line[:content_start] + quote_type + raw_line.strip()[len(quote_type):].strip() + "\n"
            else: 
                content_end = raw_line.rfind(quote_type) 
                processed_line = raw_line[:content_start] + quote_type + raw_line[content_start+len(quote_type):content_end].strip() + raw_line[content_end:]
            contents[line_index] = processed_line
        for line_num in error_lines_num:
            strip_whitespaces(contents, line_num-1)
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

    # D403: First word of the first line should be properly capitalized
    # does NOT change line numbers 
    def fix_D403(self): 
        contents = self.contents 
        error_lines_num = self.error_pairs["D403"] 
        if not error_lines_num:
            return 
        # capitalize the docstring starting at contents[line_index] 
        def capitalize_first_alpha(contents, line_index):
            while not(contain_alpha(contents[line_index])): 
                line_index += 1 
            line = contents[line_index]
            result_line_list = [] 
            for i in range(len(line)): 
                if line[i].isalpha(): 
                    result_line_list.append(line[:i])
                    result_line_list.append(line[i].upper())
                    result_line_list.append(line[i+1:])
                    break 
            contents[line_index] = "".join(result_line_list)
        # apply fix for every D403 violation in self.fname
        for line_num in error_lines_num:
            capitalize_first_alpha(contents, line_num-1)
        self.contents = contents 

    def execute(self): 
        f = open(self.fname, "r") 
        self.contents = f.readlines() 
        f.close() 

        self.error_pairs = self.generate_error_pairs()
        print_errors(self.error_pairs, "=====BEFORE=====")

        self.fix_D300()
        self.fix_D200()    
        self.fix_D210()
        self.fix_D403()
        self.fix_D400() 

        f = open(self.fname, "w")
        f.writelines(self.contents) 
        f.close() 
        self.error_pairs = self.generate_error_pairs()
        print_errors(self.error_pairs, "=====AFTER=====")    


# for testing autoDoc with a file specified through command line arguments  
if __name__ == "__main__":
    if len (sys.argv) == 2 and os.path.isfile (sys.argv[-1]): 
        obj = AutoDoc (sys.argv[-1]) 
        obj.execute () 
    else: 
        print ("ERROR: A valid file name is required.")