# autoDoc

# Current Progress
1. Fixed D200, D210, D403 
2. Generate error overview for a directory with all its sub-directories

# Ignored cases
1. Missing Docstrings: D100 - D107
2. Docstring Content Issues: D401, D402

# TODOs
* Create test cases for each fix 
* Instead of doing fileIO for each fix_D(..) function, just do it once and pass down contents 

# Implementation Choice
* The current implementation requires the files to be modified to be written somewhat reasonably
* For D400, a fix will be executed for IFF (a single-line docstring) OR (the second line that contains letters starts with a capital letter)