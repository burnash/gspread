Examples of gspread Usage
=========================

If you haven't yet authorized your app, read :doc:`oauth2` first.


Opening a Spreadsheet
~~~~~~~~~~~~~~~~~~~~~

You can open a spreadsheet by its title as it appears in Google Docs:

.. code:: python

   sh = gc.open('My poor gym results')

If you want to be specific, use a key (which can be extracted from
the spreadsheet's url):

.. code:: python

   sht1 = gc.open_by_key('0BmgG6nO_6dprdS1MN3d3MkdPa142WFRrdnRRUWl1UFE')

Or, if you feel really lazy to extract that key, paste the entire spreadsheet's url

.. code:: python

   sht2 = gc.open_by_url('https://docs.google.com/spreadsheet/ccc?key=0Bm...FE&hl')


Creating a Spreadsheet
~~~~~~~~~~~~~~~~~~~~~~

Use :meth:`~gspread.Client.create` to create a new blank spreadsheet:

.. code:: python

   sh = gc.create('A new spreadsheet')

.. NOTE::
    If you're using a :ref:`service account <service-account>`, this new spreadsheet will be
    visible only to this account. To be able to access newly created spreadsheet
    from Google Sheets with your own Google account you *must* share it with your
    email. See how to share a spreadsheet in the section below.

Sharing a Spreadsheet
~~~~~~~~~~~~~~~~~~~~~

If your email is *otto@example.com* you can share the newly created spreadsheet
with yourself:

.. code:: python

   sh.share('otto@example.com', perm_type='user', role='writer')

See :meth:`~gspread.models.Spreadsheet.share` documentation for a full list of accepted parameters.


Selecting a Worksheet
~~~~~~~~~~~~~~~~~~~~~

Select worksheet by index. Worksheet indexes start from zero:

.. code:: python

   worksheet = sh.get_worksheet(0)

Or by title:

.. code:: python

   worksheet = sh.worksheet("January")

Or the most common case: *Sheet1*:

.. code:: python

   worksheet = sh.sheet1

To get a list of all worksheets:

.. code:: python

   worksheet_list = sh.worksheets()


Creating a Worksheet
~~~~~~~~~~~~~~~~~~~~

.. code:: python

   worksheet = sh.add_worksheet(title="A worksheet", rows="100", cols="20")


Deleting a Worksheet
~~~~~~~~~~~~~~~~~~~~

.. code:: python

   sh.del_worksheet(worksheet)


Getting a Cell Value
~~~~~~~~~~~~~~~~~~~~

Using `A1 notation <https://developers.google.com/sheets/api/guides/concepts#a1_notation>`_:

.. code:: python

   val = worksheet.acell('B1').value

Or row and column coordinates:

.. code:: python

   val = worksheet.cell(1, 2).value

If you want to get a cell formula:

.. code:: python

   cell = worksheet.acell('B1', value_render_option='FORMULA').value

   # or

   cell = worksheet.cell(1, 2, value_render_option='FORMULA').value


Getting All Values From a Row or a Column
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get all values from the first row:

.. code:: python

   values_list = worksheet.row_values(1)

Get all values from the first column:

.. code:: python

   values_list = worksheet.col_values(1)

.. NOTE::
    So far we've been fetching a limited amount of data from a sheet. This works great until
    you need to get values from hundreds of cells or iterating over many rows or columns.

    Under the hood, gspread uses `Google Sheets API v4 <https://developers.google.com/sheets/api>`_.
    Most of the time when you call a gspread method to fetch or update a sheet gspread produces
    one HTTP API call.

    HTTP calls have performance costs. So if you find your app fetching values one by one in
    a loop or iterating over rows or columns you can improve the performance of the app by fetching
    data in one go.

    What's more, Sheets API v4 introduced `Usage Limits <https://developers.google.com/sheets/api/limits>`_
    (as of this writing, 500 requests per 100 seconds per project, and 100 requests per 100 seconds per user). When your
    application hits that limit, you get an :exc:`~gspread.exceptions.APIError` `429 RESOURCE_EXHAUSTED`.

    Here are the methods that may help you to reduce API calls:

        * :meth:`~gspread.models.Worksheet.get_all_values` fetches values from all of the cells of the sheet.
        * :meth:`~gspread.models.Worksheet.get` fetches all values from a range of cells.
        * :meth:`~gspread.models.Worksheet.batch_get` can fetch values from multiple ranges of cells with one API call.
        * :meth:`~gspread.models.Worksheet.update` lets you update a range of cells with a list of lists.
        * :meth:`~gspread.models.Worksheet.batch_update` lets you update multiple ranges of cells with one API call.


Getting All Values From a Worksheet as a List of Lists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   list_of_lists = worksheet.get_all_values()


Getting All Values From a Worksheet as a List of Dictionaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   list_of_dicts = worksheet.get_all_records()


Finding a Cell
~~~~~~~~~~~~~~

Find a cell matching a string:

.. code:: python

   cell = worksheet.find("Dough")

   print("Found something at R%sC%s" % (cell.row, cell.col))

Find a cell matching a regular expression

.. code:: python

   amount_re = re.compile(r'(Big|Enormous) dough')
   cell = worksheet.find(amount_re)

`find` returns `None` if value is not Found

Finding All Matched Cells
~~~~~~~~~~~~~~~~~~~~~~~~~

Find all cells matching a string:

.. code:: python

   cell_list = worksheet.findall("Rug store")

Find all cells matching a regexp:

.. code:: python

   criteria_re = re.compile(r'(Small|Room-tiering) rug')
   cell_list = worksheet.findall(criteria_re)

Clear A Worksheet
~~~~~~~~~~~~~~~~~

Clear one or multiple celle ranges at once:

.. code:: python

   worksheet.batch_clear(["A1:B1", "C2:E2", "my_named_range"])

Clear the entire workshseet:

.. code:: python

   worksheet.clear()

Cell Object
~~~~~~~~~~~

Each cell has a value and coordinates properties:

.. code:: python


   value = cell.value
   row_number = cell.row
   column_number = cell.col

Updating Cells
~~~~~~~~~~~~~~

Using `A1 notation <https://developers.google.com/sheets/api/guides/concepts#a1_notation>`_:

.. code:: python

   worksheet.update('B1', 'Bingo!')

Or row and column coordinates:

.. code:: python

   worksheet.update_cell(1, 2, 'Bingo!')

Update a range

.. code:: python

   worksheet.update('A1:B2', [[1, 2], [3, 4]])

Formatting
~~~~~~~~~~

Here's an example of basic formatting.

Set **A1:B1** text format to bold:

.. code:: python

   worksheet.format('A1:B1', {'textFormat': {'bold': True}})

Color the background of **A2:B2** cell range in black, change horizontal alignment, text color and font size:

.. code:: python

   worksheet.format("A2:B2", {
       "backgroundColor": {
         "red": 0.0,
         "green": 0.0,
         "blue": 0.0
       },
       "horizontalAlignment": "CENTER",
       "textFormat": {
         "foregroundColor": {
           "red": 1.0,
           "green": 1.0,
           "blue": 1.0
         },
         "fontSize": 12,
         "bold": True
       }
   })

The second argument to :meth:`~gspread.models.Worksheet.format` is a dictionary containing the fields to update. A full specification of format options is available at `CellFormat <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/cells#cellformat>`_ in Sheet API Reference.

.. Tip::
    `gspread-formatting <https://github.com/robin900/gspread-formatting>`_ offers extensive functionality to help you when you go beyond basics.


Using gspread with pandas
~~~~~~~~~~~~~~~~~~~~~~~~~

`pandas <https://pandas.pydata.org/>`_ is a popular library for data analysis. The simplest way to get data from a sheet to a pandas DataFrame is with :meth:`~gspread.models.Worksheet.get_all_records`:

.. code:: python

   import pandas as pd

   dataframe = pd.DataFrame(worksheet.get_all_records())

Here's a basic example for writing a dataframe to a sheet. With :meth:`~gspread.models.Worksheet.update` we put the header of a dataframe into the first row of a sheet followed by the values of a dataframe:

.. code:: python

   import pandas as pd

   worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

For advanced pandas use cases check out these libraries:

 * `gspread-pandas <https://github.com/aiguofer/gspread-pandas>`_
 * `gspread-dataframe <https://github.com/robin900/gspread-dataframe>`_

Using gspread with NumPy
~~~~~~~~~~~~~~~~~~~~~~~~

`NumPy <https://numpy.org/>`_ is a library for scientific computing in Python. It provides tools for working with high performance multi-dimensional arrays.

Read contents of a sheet into a NumPy array:

.. code:: python

   import numpy as np
   array = np.array(worksheet.get_all_values())

The code above assumes that your data starts from the first row of the sheet. If you have a header row in the first row, you need replace ``worksheet.get_all_values()`` with ``worksheet.get_all_values()[1:]``.

Write a NumPy array to a sheet:

.. code:: python

   import numpy as np

   array = np.array([[1, 2, 3], [4, 5, 6]])

   # Write the array to worksheet starting from the A2 cell
   worksheet.update('A2', array.tolist())

