# AutoDoc
A tool that automatically changes existing documentations to comply to PEP257 and the Sphinx format.

## Resources
* We used [pydocstyle](https://pypi.org/project/pydocstyle/) to detect PEP257 violations.
* Here is a reference to the [error codes](http://www.pydocstyle.org/en/2.1.1/error_codes.html).

## Current Progress
* Fixed violations: D200, D202, D204, D205, D210, D300, D301, D400, D403, D412.
* Debug mode that generates an overview for the violations for all files inside a directory. 

## Ignored Cases
1. Missing Docstrings: D100 - D107
2. Docstring Mood Issues: D401, D402

## Files
* **auto_doc.py:** contains a class that accepts a file name and apply fixes to that file. 
* **auto_helper.py:** contains helper functions for auto_doc.py.
* **auto_overview.py:** takes a directory and apply fixes to all files within the directory. 
