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