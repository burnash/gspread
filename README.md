# Google Spreadsheets Python API v4

![main workflow](https://img.shields.io/github/actions/workflow/status/burnash/gspread/main.yaml?logo=github)
![GitHub licence](https://img.shields.io/pypi/l/gspread?logo=github)
![GitHub downloads](https://img.shields.io/github/downloads-pre/burnash/gspread/latest/total?logo=github)
![documentation](https://img.shields.io/readthedocs/gspread?logo=readthedocs)
![PyPi download](https://img.shields.io/pypi/dm/gspread?logo=pypi)
![PyPi version](https://img.shields.io/pypi/v/gspread?logo=pypi)
![python version](https://img.shields.io/pypi/pyversions/gspread?style=pypi)

Simple interface for working with Google Sheets.

Features:

- Open a spreadsheet by **title**, **key** or **URL**.
- Read, write, and format cell ranges.
- Sharing and access control.
- Batching updates.

## Installation

```sh
pip install gspread
```

Requirements: Python 3.8+.

## Basic Usage

1. [Create credentials in Google API Console](http://gspread.readthedocs.org/en/latest/oauth2.html)

2. Start using gspread

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

## v5.12 to v6.0 Migration Guide

### Upgrade from Python 3.7

Python 3.7 is [end-of-life](https://devguide.python.org/versions/). gspread v6 requires a minimum of Python 3.8.

### Change `Worksheet.update` arguments

The first two arguments (`values` & `range_name`) have swapped (to `range_name` & `values`). Either swap them (works in v6 only), or use named arguments (works in v5 & v6).

As well, `values` can no longer be a list, and must be a 2D array.

```diff
- file.sheet1.update([["new", "values"]])
+ file.sheet1.update([["new", "values"]]) # unchanged

- file.sheet1.update("B2:C2", [["54", "55"]])
+ file.sheet1.update([["54", "55"]], "B2:C2")
# or
+ file.sheet1.update(range_name="B2:C2", values=[["54", "55"]])
```

### More

<details><summary>See More Migration Guide</summary>

### Change colors from dictionary to text

v6 uses hexadecimal color representation. Change all colors to hex. You can use the compatibility function `gspread.utils.convert_colors_to_hex_value()` to convert a dictionary to a hex string.

```diff
- tab_color = {"red": 1, "green": 0.5, "blue": 1}
+ tab_color = "#FF7FFF"
file.sheet1.update_tab_color(tab_color)
```

### Switch lastUpdateTime from property to method

```diff
- age = spreadsheet.lastUpdateTime
+ age = spreadsheet.get_lastUpdateTime()
```

### Replace method `Worksheet.get_records`

In v6 you can now only get *all* sheet records, using `Worksheet.get_all_records()`. The method `Worksheet.get_records()` has been removed. You can get some records using your own fetches and combine them with `gspread.utils.to_records()`.

```diff
+ from gspread import utils
  all_records = spreadsheet.get_all_records(head=1)
- some_records = spreadsheet.get_all_records(head=1, first_index=6, last_index=9)
- some_records = spreadsheet.get_records(head=1, first_index=6, last_index=9)
+ header = spreadsheet.get("1:1")[0]
+ cells = spreadsheet.get("6:9")
+ some_records = utils.to_records(header, cells)
```

### Silence warnings

In version 5 there are many warnings to mark deprecated feature/functions/methods.
They can be silenced by setting the `GSPREAD_SILENCE_WARNINGS` environment variable to `1`

### Add more data to `gspread.Worksheet.__init__`

```diff
  gc = gspread.service_account(filename="google_credentials.json")
  spreadsheet = gc.open_by_key("{{key}}")
  properties = spreadsheet.fetch_sheet_metadata()["sheets"][0]["properties"]
- worksheet = gspread.Worksheet(spreadsheet, properties)
+ worksheet = gspread.Worksheet(spreadsheet, properties, spreadsheet.id, gc.http_client)
```

</details>

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
from gspread.utils import GridRangeType
list_of_lists = worksheet.get(return_type=GridRangeType.ListOfLists)
```

### Getting a range of values

Receive only the cells with a value in them.

```python
>>> worksheet.get("A1:B4")
[['A1', 'B1'], ['A2']]
```

Receive a rectangular array around the cells with values in them.

```python
>>> worksheet.get("A1:B4", pad_values=True)
[['A1', 'B1'], ['A2', '']]
```

Receive an array matching the request size regardless of if values are empty or not.

```python
>>> worksheet.get("A1:B4", maintain_size=True)
[['A1', 'B1'], ['A2', ''], ['', ''], ['', '']]
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

## Documentation

[Documentation]\: [https://gspread.readthedocs.io/][Documentation]

[Documentation]: https://gspread.readthedocs.io/en/latest/

### Ask Questions

The best way to get an answer to a question is to ask on [Stack Overflow with a gspread tag](http://stackoverflow.com/questions/tagged/gspread?sort=votes&pageSize=50).

## Contributors

[List of contributors](https://github.com/burnash/gspread/graphs/contributors)

## How to Contribute

Please make sure to take a moment and read the [Code of Conduct](https://github.com/burnash/gspread/blob/master/.github/CODE_OF_CONDUCT.md).

### Report Issues

Please report bugs and suggest features via the [GitHub Issues](https://github.com/burnash/gspread/issues).

Before opening an issue, search the tracker for possible duplicates. If you find a duplicate, please add a comment saying that you encountered the problem as well.

### Improve Documentation

[Documentation](https://gspread.readthedocs.io/) is as important as code. If you know how to make it more consistent, readable and clear, please submit a pull request. The documentation files are in [`docs`](https://github.com/burnash/gspread/tree/master/docs) folder, use [reStructuredText](http://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html#rst-index) markup and rendered by [Sphinx](http://www.sphinx-doc.org/).

### Contribute code

Please make sure to read the [Contributing Guide](https://github.com/burnash/gspread/blob/master/.github/CONTRIBUTING.md) before making a pull request.
