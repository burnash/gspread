# Google Spreadsheets Python API

Manage your spreadsheets with _gspread_ in Python.

Features:

* Google Sheets API v4.
* Open a spreadsheet by its **title** or **url**.
* Extract range, entire row or column values.
* Python 3 support.

## Basic Usage

1. [Obtain OAuth2 credentials from Google Developers Console](http://gspread.readthedocs.org/en/latest/oauth2.html)

2. Start using gspread:

```python
import gspread

gc = gspread.authorize(credentials)

# Open a worksheet from spreadsheet with one shot
wks = gc.open("Where is the money Lebowski?").sheet1

wks.update_acell('B2', "it's down there somewhere, let me take another look.")

# Fetch a cell range
cell_list = wks.range('A1:B7')
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

### Formatting Cells

Basic formatting of a range of cells is supported. All basic formatting components 
of the v4 Sheets API's `CellFormat` are present as classes in the `gspread.format` module, 
available both by `InitialCaps` names and `camelCase` names: for example, the background color 
class is `BackgroundColor` but is also available as `backgroundColor`, while the color class is `Color`
but available also as `color`. Attributes of formatting components are best specified as 
keyword arguments using `camelCase` naming, e.g. `backgroundColor=...`. Complex formats 
may be composed easily, by nesting the calls to the classes.  

See [the CellFormat page of the Sheets API documentation](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets#CellFormat) 
to learn more about each formatting component.

```python

from gspread.format import *

fmt = cellFormat(
    backgroundColor=color(1, 0.9, 0.9),
    textFormat=textFormat(bold=True, foregroundColor=color(1, 0, 1)),
    horizontalAlignment='CENTER'
    )

ws.format_range('A1:J1', fmt)
```

`CellFormat` objects are comparable with `==` and `!=`, and are mutable at all times; 
they can be safely copied with `copy.deepcopy`. `CellFormat` objects can be combined
into a new `CellFormat` object using the `add` method (or `+` operator). `CellFormat` objects also offer 
`difference` and `intersection` methods, as well as the corresponding
operators `-` (for difference) and `&` (for intersection). An example:

```python

>>> default_format = CellFormat(backgroundColor=color(1,1,1), textFormat=textFormat(bold=True))
>>> user_format = CellFormat(textFormat=textFormat(italic=True))
>>> effective_format = default_format + user_format
>>> effective_format
CellFormat(backgroundColor=color(1,1,1), textFormat=textFormat(bold=True, italic=True))
>>> effective_format - user_format 
CellFormat(backgroundColor=color(1,1,1), textFormat=textFormat(bold=True))
>>> effective_format - user_format == default_format
True
```

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
* [Getting Google API's credentials](http://gspread.readthedocs.io/en/latest/oauth2.html)
* [gspread API Reference](http://gspread.readthedocs.org/)

## Testing

1. Go to Google Drive and create an empty spreadsheet you will use for testing.
2. Create a configuration file from config dummy:

    ```sh
    cp tests/tests.config.example tests/tests.config
    ```

3. Open `tests.config` with your favorite editor and fill up config parameters with your testing spreadsheet's info.
4. Install [Nose](http://nose.readthedocs.org).
5. Download credentials json file(see [doc](http://gspread.readthedocs.io/en/latest/oauth2.html#using-signed-credentials)),
rename it to `creds.json` and put it into the tests folder.
6. Run tests:

    ```sh
    nosetests
    ```

## [Contributors](https://github.com/burnash/gspread/graphs/contributors)

## How to Contribute

### Ask Questions

The best way to get an answer to a question is to ask on [Stack Overflow with a gspread tag](http://stackoverflow.com/questions/tagged/gspread?sort=votes&pageSize=50).

### Report Issues

Please report bugs and suggest features via the [GitHub Issues](https://github.com/burnash/gspread/issues).

Before opening an issue, search the tracker for possible duplicates. If you find a duplicate, please add a comment saying that you encountered the problem as well.

### Contribute code

* Check the [GitHub Issues](https://github.com/burnash/gspread/issues) for open issues that need attention.
* Follow the [Contributing to Open Source](https://guides.github.com/activities/contributing-to-open-source/) Guide.
