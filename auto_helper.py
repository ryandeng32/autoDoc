# return whether a line contains any alpha letter 
def contain_alpha(line): 
    for c in line: 
        if c.isalpha(): 
            return True 
    return False 

def print_errors(error_pairs, msg=None): 
    if msg: 
        print(msg) 
    output = [] 
    for error in error_pairs: 
        output.append(f"{error}: {error_pairs[error]}")
    output.sort()
    for i in output:
        print(i)