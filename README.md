# Google Spreadsheets Python API v4
![latest workflow](https://github.com/burnash/gspread/actions/workflows/main.yaml/badge.svg?branch=master)
 [![GitHub version](https://badge.fury.io/gh/burnash%2Fgspread.svg)](https://badge.fury.io/gh/burnash%2Fgspread) ![pypi]( https://badge.fury.io/py/gspread.svg) ![downloads](https://img.shields.io/pypi/dm/gspread.svg) ![doc](https://readthedocs.org/projects/gspread/badge/?version=latest)


Simple interface for working with Google Sheets.

Features:

* Open a spreadsheet by **title**, **key** or **url**.
* Read, write, and format cell ranges.
* Sharing and access control.
* Batching updates.

## Installation

```sh
pip install gspread
```

Requirements: Python 3.6+.


## Basic Usage

1. [Create credentials in Google API Console](http://gspread.readthedocs.org/en/latest/oauth2.html)

2. Start using gspread:

```python
import gspread

gc = gspread.service_account()

# Open a sheet from a spreadsheet in one go
wks = gc.open("Where is the money Lebowski?").sheet1

# Update a range of cells using the top left corner address
wks.update('A1', [[1, 2], [3, 4]])

# Or update a single cell
wks.update('B42', "it's down there somewhere, let me take another look.")

# Format the header
wks.format('A1:B1', {'textFormat': {'bold': True}})
```

## More Examples

### Opening a Spreadsheet

```python
# You can open a spreadsheet by its title as it appears in Google Docs
sh = gc.open('My poor gym results') # <-- Look ma, no keys!

# If you want to be specific, use a key (which can be extracted from
# the spreadsheet's url)
sht1 = gc.open_by_key('0BmgG6nO_6dprdS1MN3d3MkdPa142WFRrdnRRUWl1UFE')

# Or, if you feel really lazy to extract that key, paste the entire url
sht2 = gc.open_by_url('https://docs.google.com/spreadsheet/ccc?key=0Bm...FE&hl')
```

### Creating a Spreadsheet

```python
sh = gc.create('A new spreadsheet')

# But that new spreadsheet will be visible only to your script's account.
# To be able to access newly created spreadsheet you *must* share it
# with your email. Which brings us to…
```

### Sharing a Spreadsheet

```python
sh.share('otto@example.com', perm_type='user', role='writer')
```

### Selecting a Worksheet

```python
# Select worksheet by index. Worksheet indexes start from zero
worksheet = sh.get_worksheet(0)

# By title
worksheet = sh.worksheet("January")

# Most common case: Sheet1
worksheet = sh.sheet1

# Get a list of all worksheets
worksheet_list = sh.worksheets()
```

### Creating a Worksheet

```python
worksheet = sh.add_worksheet(title="A worksheet", rows="100", cols="20")
```

### Deleting a Worksheet

```python
sh.del_worksheet(worksheet)
```

### Getting a Cell Value

```python
# With label
val = worksheet.get('B1').first()

# With coords
val = worksheet.cell(1, 2).value
```

### Getting All Values From a Row or a Column

```python
# Get all values from the first row
values_list = worksheet.row_values(1)

# Get all values from the first column
values_list = worksheet.col_values(1)
```

### Getting All Values From a Worksheet as a List of Lists

```python
list_of_lists = worksheet.get_values()
```

### Finding a Cell

```python
# Find a cell with exact string value
cell = worksheet.find("Dough")

print("Found something at R%sC%s" % (cell.row, cell.col))

# Find a cell matching a regular expression
amount_re = re.compile(r'(Big|Enormous) dough')
cell = worksheet.find(amount_re)
```

### Finding All Matched Cells

```python
# Find all cells with string value
cell_list = worksheet.findall("Rug store")

# Find all cells with regexp
criteria_re = re.compile(r'(Small|Room-tiering) rug')
cell_list = worksheet.findall(criteria_re)
```

### Updating Cells

```python
# Update a single cell
worksheet.update('B1', 'Bingo!')

# Update a range
worksheet.update('A1:B2', [[1, 2], [3, 4]])

# Update multiple ranges at once
worksheet.batch_update([{
    'range': 'A1:B2',
    'values': [['A1', 'B1'], ['A2', 'B2']],
}, {
    'range': 'J42:K43',
    'values': [[1, 2], [3, 4]],
}])
```

## [Documentation](https://gspread.readthedocs.io/en/latest/)

## [Contributors](https://github.com/burnash/gspread/graphs/contributors)

## How to Contribute

Please make sure to take a moment and read the [Code of Conduct](https://github.com/burnash/gspread/blob/master/.github/CODE_OF_CONDUCT.md).

### Ask Questions

The best way to get an answer to a question is to ask on [Stack Overflow with a gspread tag](http://stackoverflow.com/questions/tagged/gspread?sort=votes&pageSize=50).

### Report Issues

Please report bugs and suggest features via the [GitHub Issues](https://github.com/burnash/gspread/issues).

Before opening an issue, search the tracker for possible duplicates. If you find a duplicate, please add a comment saying that you encountered the problem as well.

### Improve Documentation

[Documentation](https://gspread.readthedocs.io/) is as important as code. If you know how to make it more consistent, readable and clear, please submit a pull request. The documentation files are in [`docs`](https://github.com/burnash/gspread/tree/master/docs) folder, use [reStructuredText](http://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html#rst-index) markup and rendered by [Sphinx](http://www.sphinx-doc.org/).

### Contribute code

Please make sure to read the [Contributing Guide](https://github.com/burnash/gspread/blob/master/.github/CONTRIBUTING.md) before making a pull request.
