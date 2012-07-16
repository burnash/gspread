# gspread

Python Google Spreadsheets library with simple API.

Features:

* Open a spreadsheet by its **title** or **url**.
* Extract range, entire row or column values.
* Independent of Google Data Python client library.
* Python 3 support.

## Basic usage

```python
import gspread

# Login with your Google account
gc = gspread.login('thedude@abid.es','password')

# Open a worksheet from spreadsheet with one shot
wks = gc.open("Where is the money Lebowski?").sheet1

wks.update_acell('B2', "it's down there somewhere, let me take another look.")
```

## More examples

### Opening a spreadsheet

```python
# You can open a spreadsheet by its title as it appers in Google Docs
sh = gc.open("My poor gym results") # <-- Look ma, no keys!

# If you want to be specific, use a key (which can be extracted from
# the spreadsheet's url)
sht1 = gc.open_by_key('0BmgG6nO_6dprdS1MN3d3MkdPa142WFRrdnRRUWl1UFE')

# Or, if you feel really lazy to extract that key, paste the entire url
sht2 = gc.open_by_url('https://docs.google.com/spreadsheet/ccc?key=0Bm...FE&hl')
```

### Selecting a worksheet

```python
# Select worksheet by index. Worksheet indexes start from zero
worksheet = sh.get_worksheet(0)

# Most common case: Sheet1
worksheet = sh.sheet1
```

### Getting a cell value

```python
# With label
val = worksheet.acell('B1').value

# With coords
val = worksheet.cell(1, 2).value

# Get all values from column. Column and row indexes start from one
first_col = worksheet.col_values(1)
```

### Finding a cell

```python
# Find a cell with exact string value
cell = worksheet.find("Dough")

# Find a cell matching a regular expression
amount_re = re.compile(r'(Big|Enormous) dough')
cell = worksheet.find(amount_re)

# Find all cells
cell_list = worksheet.findall(amount_re)
```

### Updating

```python
worksheet.update_acell('B1', 'Bingo!')

# Or
worksheet.update_cell(1, 2, 'Bingo!')

# Select a range
cell_list = worksheet.range('A1:A7')

for cell in cell_list:
    cell.value = 'O_o'

# Update in batch
worksheet.update_cells(cell_list)
```

## Requirements

Python 2.6+ or Python 3+

## Installation

### From GitHub

```sh
git clone https://github.com/burnash/gspread.git
cd gspread
python setup.py install
```

### From PyPI

```sh
pip install gspread
```

If you're on easy_install, it's:

```sh
easy_install gspread
```

## Documentation

[Docs on GitHub](http://burnash.github.com/gspread/)

## Suggestions & Code Contribution

- [Javier Candeira](https://github.com/candeira)
- [Peter "Mash" Morgan](https://github.com/ac001)
- [ptlu](https://github.com/ptlu)

## Feedback

The library is in active development so any feedback is *urgently* needed. Please
don't hesitate to open up a new [github issue](https://github.com/burnash/gspread/issues)
or simply drop me a line to <fuss.here@gmail.com>.
