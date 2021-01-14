import subprocess 
from collections import defaultdict

class AutoDoc: 
    def __init__(self, fname): 
        self.fname = fname
        self.error_pairs = self.generate_error_pairs()
    
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
    
    # D403: First word of the first line should be properly capitalized
    def fix_D403(self): 
        error_lines_num = self.error_pairs["D403"]
        f = open(self.fname, "r")
        contents = f.readlines() 
        f.close()
        def capitalize_first_alpha(line):
            result_line_list = [] 
            for i in range(len(line)): 
                if line[i].isalpha(): 
                    result_line_list.append(line[:i])
                    result_line_list.append(line[i].upper())
                    result_line_list.append(line[i+1:])
                    break 
            return "".join(result_line_list)
        for line_num in error_lines_num:
            contents[line_num-1] = capitalize_first_alpha(contents[line_num-1])
        f = open(self.fname, "w")    
        f.writelines(contents)
        f.close()

obj = AutoDoc("random_file.py") 
print(obj.error_pairs)
obj.fix_D403()

