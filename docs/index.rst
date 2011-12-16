.. gspread documentation master file, created by
   sphinx-quickstart on Thu Dec 15 14:44:32 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

gspread — Google Spreadsheets Python library
============================================

gspread is a client library for interacting with `Google Spreadsheets`_.

.. _Google Spreadsheets: http://www.google.com/google-d-s/spreadsheets/

Features
--------

* Open a spreadsheet by its *title*, *url* or *key*.
* Extract range, entire row or column values.
* Independent of Google Data Python client library.

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

