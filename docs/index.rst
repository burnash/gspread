.. gspread documentation master file, created by
   sphinx-quickstart on Thu Dec 15 14:44:32 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

gspread — Google Spreadsheets Python library
============================================

Contents:

.. toctree::
   :maxdepth: 2

   reference

Example
-------

The following code is a Python program that connects to Google Data API
and fetches a cell's value from a spreadsheet::

    import gspread

    gc = gspread.Client(auth=('the.email.address@gmail.com','password'))
    gc.login()

    # Spreadsheets can be opened by their title in Google Docs
    spreadsheet = gc.open('some title')

    # Select worksheet by index
    worksheet = spreadsheet.get_worksheet(0)

    # Get a cell value
    val = worksheet.cell(1, 2).value

The cell's value can be easily updated::

    worksheet.update_cell(1, 2, 'Bingo!')

To fetch a cell range, specify it by common notation::

    cell_list = worksheet.range('A1:A7')

After some processing, this range can be updated in batch::

    worksheet.update_cells(cell_list)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

