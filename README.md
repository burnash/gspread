# Google Spreadsheets Python API
[![Downloads](https://pypip.in/d/gspread/badge.png)](https://crate.io/packages/gspread)

Manage your spreadsheets with _gspread_ in Python.

Features:

* Open a spreadsheet by its **title** or **url**.
* Extract range, entire row or column values.
* Independent of Google Data Python client library.
* Python 3 support.

![logo](https://raw.github.com/burnash/gspread/master/gspread.png "")

## Basic Usage

```python
import gspread

# Login with your Google account
gc = gspread.login('thedude@abid.es', 'password')

# WARNING: The code above uses ClientLogin and was disabled 
# on April 20, 2015.

# Please use OAuth2 authorization to access Google Sheets.

# Open a worksheet from spreadsheet with one shot
wks = gc.open("Where is the money Lebowski?").sheet1

wks.update_acell('B2', "it's down there somewhere, let me take another look.")

# Fetch a cell range
cell_list = wks.range('A1:B7')
```

## Authorization Using OAuth2

```python
import gspread

# Login with your Google account
gc = gspread.authorize(OAuth2Credentials)

# Open a worksheet from spreadsheet with one shot
wks = gc.open("Where is the money Lebowski?").sheet1

```

OAuth2Credentials must be an object with a valid `access_token` attribute, such as one created with the oauth2client library from Google. See ["Using OAuth2 for Authorization"](http://gspread.readthedocs.org/en/latest/oauth2.html) for more information.

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

[API Reference](http://gspread.readthedocs.org/)

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

## Testing environment setup

    pip install nose
    pip install requests['security']
    pip install oath2client

## Suggestions & Code Contribution

- [Javier Candeira](https://github.com/candeira)
- [Peter "Mash" Morgan](https://github.com/ac001)
- [ptlu](https://github.com/ptlu)
- [aginor](https://github.com/aginor)

[All contributors](https://github.com/burnash/gspread/graphs/contributors)

## Feedback

Please report bugs and suggest features via [GitHub Issues](https://github.com/burnash/gspread/issues).
