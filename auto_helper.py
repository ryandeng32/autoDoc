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
    quote_types = ['"""', "'''", '"', "'"] 
    curr_type = None 
    first_line = contents[line_index].strip() 
    for quote_type in quote_types: 
        if first_line.find(quote_type) == 0: 
            curr_type = quote_type
            break 
    if curr_type == "'" or curr_type == '"' or (first_line.count(curr_type) >= 2 and first_line.rfind(curr_type) == len(first_line) - 3): 
        return (line_index, curr_type, contents[line_index])
    start, end = line_index, line_index + 1
    # find the end of docstring 
    while curr_type not in contents[end]: 
        end += 1 
    raw_docstring = "".join(contents[start: end+1])
    return (end, curr_type, raw_docstring)