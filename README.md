# gspread

This is a simple Python library for accessing Google Spreadsheets.

Features:

* Open a spreadsheet by its **title** or **url**.
* Extract range, entire row or column values.
* Independent of Google Data Python client library.

## Usage

~~~python
import gspread

# Login with your Google account
gc = gspread.login('account@gmail.com','password')

# Spreadsheets can be opened by their title in Google Docs
spreadsheet = gc.open("where's all the money gone 2011")

# If you want to be specific, use a key (which can be extracted from
# the spreadsheet's url
sht1 = gc.open_by_key('0BmgG6nO_6dprdS1MN3d3MkdPa142WFRrdnRRUWl1UFE')

# Or, if you feel really lazy to extract that key, paste the entire url
sht2 = gc.open_by_url('https://docs.google.com/spreadsheet/ccc?key=0Bm...FE&hl')

# Select worksheet by index. Worksheet indexes start from zero
worksheet = spreadsheet.get_worksheet(0)

# Column and row indexes start from one
first_col = worksheet.col_values(1)

# Get a cell value
val = worksheet.cell(1, 2).value

worksheet.update_cell(1, 2, 'Bingo!')

# Select a range
cell_list = worksheet.range('A1:A7')

for cell in cell_list:
    cell.value = 'O_o'

# Update in batch
worksheet.update_cells(cell_list)

~~~
## Requirements

Python 2.6+

## Installation

### From Pypi

~~~sh
pip install gspread
~~~

If you're on easy_install, it's:

~~~sh
easy_install gspread
~~~

### From github

~~~sh
git clone https://github.com/burnash/gspread.git
cd gspread
python setup.py install
~~~

## Documentation

[Docs on GitHub](http://burnash.github.com/gspread/)


## Feedback and contribution

The library is in active development so any feedback is *urgently* needed. Please
don't hesitate to open up a new [github issue](https://github.com/burnash/gspread/issues)
or simply drop me a line to <fuss.here@gmail.com>.
