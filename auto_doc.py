import subprocess 
from collections import defaultdict


def generate_error_pair(fname): 
    # run pydocstyle
    process = subprocess.run(['pydocstyle', fname], 
                            stdout=subprocess.PIPE)
    process
    errors = [error.strip() for error in process.stdout.decode("utf-8").split("\n")]
    error_pair = defaultdict(list) 
    for i in range(len(errors) // 2):
        index = i * 2
        line_num = errors[index].split(" ")[0][len(fname)+1:]
        error_pair[line_num].append(errors[index+1][:4])
    return error_pair

error_pair = generate_error_pair("schedule.py")
print(error_pair)


# f = open("random_file.py", "r")
# contents = f.readlines() 
# f.close()

# contents.insert(0, "HI\n")
# f = open("random_file.py", "w")
# f.writelines(contents)
# f.close()