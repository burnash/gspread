# gspread

This is a simple Python library for accessing Google Spreadsheets.

Features:
 * Open a spreadsheet by its *title*.
 * Extract entire row or column values.
 * No need to mess around with spreadsheets' keys

## Usage

~~~python
import gspread

gc = gspread.Client(auth=('the.email.address@gmail.com','password'))
gc.login()

# Spreadsheets can be opened by their title in Google Docs
spreadsheet = gc.open('some title')

# Select worksheet by index. Worksheet indexes start from zero
worksheet = spreadsheet.get_worksheet(0)

# Column and row indexes start from one
first_col = worksheet.col_values(1)

worksheet.update_cell(1, 2, 'Bingo!')
~~~
