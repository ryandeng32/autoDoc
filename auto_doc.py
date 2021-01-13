import subprocess 
from collections import defaultdict

class AutoDoc: 
    def __init__(self, fname): 
        self.fname = fname
    
    def generate_error_pair(self): 
        # run pydocstyle
        process = subprocess.run(['pydocstyle', self.fname], stdout=subprocess.PIPE)
        process
        errors = [error.strip() for error in process.stdout.decode("utf-8").split("\n")]
        error_pair = defaultdict(list) 
        for i in range(len(errors) // 2):
            index = i * 2
            # line number 
            line_num = int(errors[index].split(" ")[0][len(self.fname)+1:])
            # error code 
            error_pair[errors[index+1][:4]].append(line_num)
        return error_pair

obj = AutoDoc("random_file.py") 
obj.error_pair = obj.generate_error_pair()



