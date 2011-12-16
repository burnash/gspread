.. gspread documentation master file, created by
   sphinx-quickstart on Thu Dec 15 14:44:32 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

gspread — Google Spreadsheets Python library
============================================

`gspread <https://github.com/burnash/gspread>`_ is a super simple library
for interacting with `Google Spreadsheets`_.

.. _Google Spreadsheets: http://www.google.com/google-d-s/spreadsheets/

Features
--------

* Open a spreadsheet by its *title*, *url* or *key*.
* Select cells by labels, e.g. 'A1'.
* Extract range, entire row or column values.
* Independent of Google Data Python client library.

Example
-------

This code will connect to Google Data API
and fetch a cell's value from a spreadsheet::

    import gspread

    # Login with your Google account
    gc = gspread.login('account@gmail.com','password')

    # Spreadsheets can be opened by their title in Google Docs
    spreadsheet = gc.open("where's all the money gone 2011")

    # Get a first worksheet
    worksheet = spreadsheet.sheet1

    # Get a cell value
    val = worksheet.acell('B1').value

    # Or
    val = worksheet.cell(1, 2).value

The cell's value can be easily updated::

    worksheet.update_acell('B1', 'Bingo!')

    # Or
    worksheet.update_cell(1, 2, 'Bingo!')

To fetch a cell range, specify it by common notation::

    cell_list = worksheet.range('A1:A7')

After some processing, this range can be updated in batch::

    for cell in cell_list:
        cell.value = 'O_o'

    worksheet.update_cells(cell_list)


Installation
------------

From Pypi
^^^^^^^^^
::

    pip install gspread

If you're on easy_install, it's::

    easy_install gspread


From github
^^^^^^^^^^^
::

    git clone https://github.com/burnash/gspread.git
    cd gspread
    python setup.py install


Reference
=========
.. toctree::
   :maxdepth: 2

   reference

Code
====

Check `gspread on GitHub <https://github.com/burnash/gspread>`_.

Any feedback is more than welcome: open up a new `github issue`_ and I'll be dancing
like crazy.

.. _github issue: https://github.com/burnash/gspread/issues

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

