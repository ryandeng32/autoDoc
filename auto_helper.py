# return whether a line contains any alpha letter 
def contain_alpha(line): 
    for c in line: 
        if c.isalpha(): 
            return True 
    return False 

def get_first_alpha_index(contents, line_index): 
    while not(contain_alpha(contents[line_index])): 
        line_index += 1 
    return line_index

def print_errors (error_pairs, msg=None): 
    """Print error pairs from auto_doc with an optional message to display."""
    if msg: 
        print (f"-----{msg}-----") 

    output = [] 
    for error in error_pairs: 
        output.append (f"{error}: {error_pairs[error]}")

    output.sort ()
    for i in output:
        print (i)
    print("")

def get_quote_type(line): 
    quote_types = ['"""', "'''", '"', "'"] 
    curr_type = None 
    first_line = line.strip() 
    for quote_type in quote_types: 
        if first_line.find(quote_type) == 0: 
            curr_type = quote_type
            break 
    return curr_type 

def first_non_whitespace_index(line): 
    return len(line) - len(line.lstrip())

def extract_docstring(contents, line_index): 
    first_line = contents[line_index].strip()
    curr_type = get_quote_type(contents[line_index]) 
    if curr_type == "'" or curr_type == '"' or (first_line.count(curr_type) >= 2 and first_line.rfind(curr_type) == len(first_line) - 3): 
        return (line_index, line_index, contents[line_index])
    start, end = line_index, line_index + 1
    # find the end of docstring 
    while curr_type not in contents[end]: 
        end += 1 
    raw_docstring = "".join(contents[start: end+1])
    return (start, end, raw_docstring)

def adjust_line_num(contents, error_pairs, log): 
    for error, list_line_nums in error_pairs.items():
        for i in range(len(list_line_nums)):
            num = list_line_nums[i] 
            for log_pair in log: 
                if num - 1 > log_pair[0]: 
                    num -= log_pair[1] 
                else: 
                    break 
            list_line_nums[i] = num 
        error_pairs[error] = list_line_nums
            
        

