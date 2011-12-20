User Guide
==========

Installation
------------

There are two options for installing *gspread*. The library is in active
development now, so the recommended way is to check out the source from
GitHub and to pull new updates from time to time.

From GitHub
^^^^^^^^^^^
::

    git clone https://github.com/burnash/gspread.git
    cd gspread
    python setup.py install

To get updates::

    cd gspread
    git pull
    python setup.py install


From Pypi
^^^^^^^^^

The alternative way is to install from the Python Package Index::

    pip install gspread --upgrade

And if you're on easy_install, it's::

    easy_install -U gspread


Quickstart
----------

Signing In
^^^^^^^^^^
To start working with your Google spreadsheets you need to sign in
to the service. This can be done with your Google Account::

    gc = gspread.login('account@gmail.com','password')


Openning A Spreadsheet
^^^^^^^^^^^^^^^^^^^^^^

One of the main features of `gspread` is the ability to easily open
a spreadsheet by its title. Assuming you have a spreadsheet named
"Annual report" in list of your Google Docs, you can do following
to open it up in your Python code::

    spreadsheet = gc.open("Annual report")

Pretty easy. However, Google Docs allows you to have more than one
spreadsheet under the same name. What will happen in this case?
Well, in this case the :meth:`~gspread.Client.open` method will return
the first spreadsheet it finds with this name. This is a rare case, since
you really don't want to have many documents with the same name.

For those who want to be totally specific while opening a document other
methods exist. First one is to use unique key assigned to every
Google Docs document. You can see it in the browser's address bar
when you working with your spreadsheet::

    https://docs.google.com/spreadsheet/ccc?key=1AkgN6IO_5rdrprh0V1pQVjFlQ2mIUDd3VTZ3ZjJubWc#gid=0

In this case the key is ``0AkgM6iO_6dprdHF0V1pQVjFlQ2FIUDd0VTZ3ZjJubWc``.
And the code to use to open this spreadsheet will be::

    spreadsheet = gc.open_by_key('0AkgM6iO_6dprdHF0V1pQVjFlQ2FIUDd0VTZ3ZjJubWc')

If you're somewhat lazy person (like I am), you can copy the entire
spreadsheet's url from address bar and paste it into another useful
method, called :meth:`~gspread.Client.open_by_url`::

    spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheet/ccc?key=1AkgN6IO_5rdrprh0V1pQVjFlQ2mIUDd3VTZ3ZjJubWc#gid=0")


Selecting A Worksheet
^^^^^^^^^^^^^^^^^^^^^

Each `spreadsheet` consists of one or many `worksheets` (also called `sheets`).
This is a next step in container hierarchy. Worksheets can be selected by title
or index.
In my point of view, the greatest percentage of spreadsheets have
only one worksheet (called *Sheet1* by default). For this common case
:class:`~gspread.Spreadsheet` object got a handy shortcut property :attr:`~gspread.Spreadsheet.sheet1`::

    # This will select first worksheet
    worksheet = spreadsheet.sheet1

Other options::

    # By title
    worksheet = spreadsheet.worksheet("January")

    # By index
    worksheet = spreadsheet.get_worksheet(0)

Worksheet indexes start from zero. To get a list of all worksheets::

    worksheets_list = spreadsheet.worksheets()


Getting A Cell
^^^^^^^^^^^^^^

Obviously, selecting a worksheet is not enough. Your primary target
is cells. A cell address can be represented in 2 ways:

* Colum and row number.
* An alphanumerical label, e.g. 'A1'.

To get a cell by row and column numbers, you need to call
:meth:`~gspread.Worksheet.cell` method of the :class:`worksheet <gspread.Worksheet>` object
we already have::

    # Get a cell object from row 1, column 2
    cell = worksheet.cell(1, 2)

This will return an instance of a :class:`~gspread.Cell` class.
The cell's value is in corresponding object's property::

    value = cell.value

Another way of getting a cell object is by using alphanumeric notation common to
spreadsheet software, e.g. 'B1'::

    # Get a cell object by label. This will select a cell object
    # from row 1, column 2
    cell = worksheet.acell('B1')


Getting The Entire Row Or Column
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you need the entire row values, getting all cell by cell is a very ineffective way.
To address this, :class:`gspread.Worksheet` got two methods::

    # Get the entire column values
    first_col = worksheet.col_values(1)

    # Get the entire row values
    second_row = worksheet.row_values(2)

Note, that column and row indexes in this case (as in case of :meth:`~gspread.Worksheet.cell`
method) start from 1.


Selecting A Cell Range
^^^^^^^^^^^^^^^^^^^^^^

If you want to select multiple cells at once, there's handy method for this::

    # Get a range
    cell_list = worksheet.range('A1:A7')

If you're familiar with spreadsheet software, you've probably mentioned that the
argument to this method is range address in a commonly used notation.
This call will return a list of :class:`~gspread.Cell` objects from `A` column
and first to seven rows.


Updating Cells
^^^^^^^^^^^^^^

After getting all this values from cells, and doing some useful calculations, you
may want to put some values back to the worksheet.

In case it's just a single cell value you want to update, these two methods will be
fine::

    worksheet.update_acell('B1', 'Bingo!')

    worksheet.update_cell(1, 2, 'Bingo!')

The former is using alphanumeric notation as a cell address, and the latter is accepting
integer coordinates.

Each of this two method will send an update command to Google's server for single
cell, which is pretty innefective in case you have more than one cell to update.

Enter the **batch update**::

    # First we need to get some cell objects
    cell_list = worksheet.range('A1:A7')

    # Then update the value parameter of this cells
    for cell in cell_list:
        cell.value = 'O_o'

    # And finally update them in batch
    worksheet.update_cells(cell_list)

As you may have noticed, the library interface is pretty simple. For a detailed
description of API, please proceed to the :ref:`API Reference <reference>`.
