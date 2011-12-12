# gspread

This is a simple Python library for accessing Google Spreadsheets.

Features:

* Open a spreadsheet by its **title** or **url**.
* Extract entire row or column values.
* No need to mess around with spreadsheets' keys.
* Independent of Google Data Python client library.

## Usage

~~~python
import gspread

gc = gspread.Client(auth=('the.email.address@gmail.com','password'))
gc.login()

# Spreadsheets can be opened by their title in Google Docs
spreadsheet = gc.open('some title')

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
