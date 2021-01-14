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
    
def extract_docstring(contents, line_index): 
    if contents[line_index].count('"""') == 2: 
        return (line_index, line_index, contents[line_index])
    start, end = line_index, line_index + 1
    # find the end of docstring 
    while '"""' not in contents[end]: 
        end += 1 
    raw_docstring = "".join(contents[start: end+1])
    return (start, end, raw_docstring)