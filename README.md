# Excel Order Filename Renamer

Preview and confirm moving an order number to the front of Excel filenames; collision-safe Windows utility.

Python 3.10+, standard library only. Run `python rename_orders.py "path/to/folder"`.
The program previews supported Excel filenames, requests y/N confirmation and skips existing targets.
It does not open or inspect workbook contents. Windows is the intended filesystem environment.
Keep real workbooks out of Git; try the program on a copy first.

See VALIDATION.md for actual checks.
