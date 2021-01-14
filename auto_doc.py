import subprocess 
from collections import defaultdict
from auto_helper import contain_alpha, print_errors, extract_docstring

class AutoDoc: 
    def __init__(self, fname): 
        self.fname = fname
        self.error_pairs = None
    
    def generate_error_pairs(self): 
        # run pydocstyle
        process = subprocess.run(['pydocstyle', self.fname], stdout=subprocess.PIPE)
        process
        errors = [error.strip() for error in process.stdout.decode("utf-8").split("\n")]
        error_pairs = defaultdict(list) 
        for i in range(len(errors) // 2):
            index = i * 2
            # line number 
            line_num = int(errors[index].split(" ")[0][len(self.fname)+1:])
            # error code 
            error_pairs[errors[index+1][:4]].append(line_num)
        return error_pairs
    
    # D200: One-line docstring should fit on one line with quotes
    # change line numbers 
    def fix_D200(self): 
        f = open(self.fname, "r") 
        contents = f.readlines() 
        f.close() 
        error_lines_num = self.generate_error_pairs()["D200"] 
        # make one-line docstring fit on one line
        def make_single_line(contents, line_index): 
            start, end, raw_docstring = extract_docstring(contents, line_index) 
            content_start = raw_docstring.find('"""')
            processed_docstring = raw_docstring[:content_start] + '"""' + raw_docstring.strip()[3:-3].strip() + '"""\n'
            # remove original docstring and insert new docstring
            for i in range(end - start + 1): 
                contents.pop(start)
            contents.insert(start, processed_docstring)
            for i in range(len(error_lines_num)): 
                error_lines_num[i] -= end - start
        # apply fix for every D200 violation in self.fname
        for i in range(len(error_lines_num)): 
            make_single_line(contents, error_lines_num[i] - 1) 
        f = open(self.fname, "w")    
        f.writelines(contents)
        f.close()

    # No whitespaces allowed surrounding docstring text
    # does NOT change line numbers 
    def fix_D210(self): 
        f = open(self.fname, "r") 
        contents = f.readlines() 
        f.close() 
        error_lines_num = self.generate_error_pairs()["D210"] 
        # strip the whitespaces in docstring's first line
        def strip_whitespaces(contents, line_index):
            raw_line = contents[line_index] 
            content_start = raw_line.find('"""')
            processed_line = raw_line[:content_start] + '"""' + raw_line.strip()[3:].strip() + "\n"
            contents[line_index] = processed_line
        for line_num in error_lines_num:
            strip_whitespaces(contents, line_num-1)
        f = open(self.fname, "w")    
        f.writelines(contents)
        f.close()

    # First line should end with a period
    # does NOT change ine numbers
    # rely on calling: fix_D200
    # @TODO fix and refactor code for case 2
    def fix_D400(self): 
        f = open(self.fname, "r") 
        contents = f.readlines() 
        f.close() 
        error_lines_num = self.generate_error_pairs()["D400"] 
        # add period for specific cases 
        def add_period(contents, line_index): 
            # case 1: one-line docstring
            start, end, _ = extract_docstring(contents, line_index) 
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
                while not(contain_alpha(contents[line_index])): 
                    line_index += 1            
                if contents[line_index].strip()[0].isupper(): 
                    contents[first_line_num] = contents[first_line_num][:-1] + ".\n"
        for line_num in error_lines_num:
            add_period(contents, line_num-1)
        f = open(self.fname, "w")    
        f.writelines(contents)
        f.close() 

    # D403: First word of the first line should be properly capitalized
    # does NOT change line numbers 
    def fix_D403(self): 
        error_lines_num = self.generate_error_pairs()["D403"] 
        f = open(self.fname, "r")
        contents = f.readlines() 
        f.close()
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
        f = open(self.fname, "w")    
        f.writelines(contents)
        f.close()

if __name__ == "__main__":
    obj = AutoDoc("./fold/random_file.py") 
    output = [] 
    obj.error_pairs = obj.generate_error_pairs()
    print_errors(obj.error_pairs, "=====BEFORE=====")
    
    obj.fix_D200() 
    obj.fix_D210()
    obj.fix_D403()
    obj.fix_D400()

    obj.error_pairs = obj.generate_error_pairs()
    print_errors(obj.error_pairs, "=====AFTER=====")

