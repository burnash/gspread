# Google Spreadsheets Python API

Manage your spreadsheets with _gspread_ in Python.

Features:

* Open a spreadsheet by its **title** or **url**.
* Extract range, entire row or column values.
* Independent of Google Data Python client library.
* Python 3 support.

## Basic Usage

1. [Obtain OAuth2 credentials from Google Developers Console](http://gspread.readthedocs.org/en/latest/oauth2.html)
<<<<<<< HEAD

2. Start using gspread:

```python
import gspread
=======

2. Start using gspread:

```python
import gspread

gc = gspread.authorize(credentials)

# WARNING: The code above uses ClientLogin and was disabled 
# on April 20, 2015.
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205

# Please use OAuth2 authorization to access Google Sheets.
=======
>>>>>>> Update README.md

gc = gspread.authorize(credentials)
>>>>>>> Update README.md

# Open a worksheet from spreadsheet with one shot
wks = gc.open("Where is the money Lebowski?").sheet1

wks.update_acell('B2', "it's down there somewhere, let me take another look.")

# Fetch a cell range
cell_list = wks.range('A1:B7')
```

<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
<<<<<<< HEAD
=======
>>>>>>> Update README.md
## Authorization Using OAuth2

```python
import gspread

# Login with your Google account
gc = gspread.authorize(OAuth2Credentials)

# Open a worksheet from spreadsheet with one shot
wks = gc.open("Where is the money Lebowski?").sheet1

```

OAuth2Credentials must be an object with a valid `access_token` attribute, such as one created with the oauth2client library from Google. See ["Using OAuth2 for Authorization"](http://gspread.readthedocs.org/en/latest/oauth2.html) for more information.

<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
>>>>>>> Update README.md
>>>>>>> Update README.md
## More Examples

### Opening a Spreadsheet

```python
# You can open a spreadsheet by its title as it appears in Google Docs
sh = gc.open("My poor gym results") # <-- Look ma, no keys!

# If you want to be specific, use a key (which can be extracted from
# the spreadsheet's url)
sht1 = gc.open_by_key('0BmgG6nO_6dprdS1MN3d3MkdPa142WFRrdnRRUWl1UFE')

# Or, if you feel really lazy to extract that key, paste the entire url
sht2 = gc.open_by_url('https://docs.google.com/spreadsheet/ccc?key=0Bm...FE&hl')
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
val = worksheet.acell('B1').value

# With coords
val = worksheet.cell(1, 2).value

# To get a cell formula
cell = worksheet.acell('B1') # or .cell(1, 2)
cell.input_value
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
list_of_lists = worksheet.get_all_values()
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

### Cell Object

Each cell has a value and coordinates properties.

```python

value = cell.value
row_number = cell.row
column_number = cell.col
```

### Updating Cells

```python
worksheet.update_acell('B1', 'Bingo!')

# Or
worksheet.update_cell(1, 2, 'Bingo!')

# Select a range
cell_list = worksheet.range('A1:C7')

for cell in cell_list:
    cell.value = 'O_o'

# Update in batch
worksheet.update_cells(cell_list)
```

<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
## Requirements

Python 2.6+ or Python 3+

>>>>>>> # This is a combination of 2 commits.
## Installation

### Requirements

Python 2.6+ or Python 3+

### From PyPI

```sh
pip install gspread
```

### From GitHub

```sh
git clone https://github.com/burnash/gspread.git
cd gspread
python setup.py install
```

## Documentation
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
* [Getting Google API's credentials](http://gspread.readthedocs.io/en/latest/oauth2.html)
* [gspread API Reference](http://gspread.readthedocs.org/)
=======

[API Reference](http://gspread.readthedocs.org/)
>>>>>>> # This is a combination of 2 commits.

## Testing

1. Go to Google Drive and create an empty spreadsheet you will use for testing.
2. Create a configuration file from config dummy:

    ```sh
    cp tests/tests.config.example tests/tests.config
    ```

3. Open `tests.config` with your favorite editor and fill up config parameters with your testing spreadsheet's info.
4. Install [Nose](http://nose.readthedocs.org).
5. Run tests:

    ```sh
    nosetests
    ```

## [Contributors](https://github.com/burnash/gspread/graphs/contributors)

## How to Contribute

### Ask Questions

The best way to get an answer to a question is to ask on [Stack Overflow with a gspread tag](http://stackoverflow.com/questions/tagged/gspread?sort=votes&pageSize=50).

### Report Issues
<<<<<<< HEAD

Please report bugs and suggest features via the [GitHub Issues](https://github.com/burnash/gspread/issues).

Before opening an issue, search the tracker for possible duplicates. If you find a duplicate, please add a comment saying that you encountered the problem as well.

<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
<<<<<<< HEAD
>>>>>>> # This is a combination of 2 commits.
### Contribute code
=======
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======

Please report bugs and suggest features via the [GitHub Issues](https://github.com/burnash/gspread/issues).

Before opening an issue, search the tracker for possible duplicates. If you find a duplicate, please add a comment saying that you encountered the problem as well.

<<<<<<< HEAD
### Contribute code
=======
>>>>>>> Update README.md
[All contributors](https://github.com/burnash/gspread/graphs/contributors)

## Feedback
>>>>>>> # This is a combination of 2 commits.
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
>>>>>>> Update README.md
>>>>>>> Update README.md

* Check the [GitHub Issues](https://github.com/burnash/gspread/issues) for open issues that need attention.
* Follow the [Contributing to Open Source](https://guides.github.com/activities/contributing-to-open-source/) Guide.
