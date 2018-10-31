More examples of gspread usage
==============================

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

However, this new spreadsheet will be visible only to your script's account.
To be able to access newly created spreadsheet you *must* share it
with your email. Which brings us to…


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


Getting All Values From a Worksheet as a List of Lists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   list_of_lists = worksheet.get_all_values()


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


Finding All Matched Cells
~~~~~~~~~~~~~~~~~~~~~~~~~

Find all cells matching a string:

.. code:: python

   cell_list = worksheet.findall("Rug store")

Find all cells matching a regexp:

.. code:: python

   criteria_re = re.compile(r'(Small|Room-tiering) rug')
   cell_list = worksheet.findall(criteria_re)

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

   worksheet.update_acell('B1', 'Bingo!')

Or row and column coordinates:

.. code:: python

   worksheet.update_cell(1, 2, 'Bingo!')

A more complicated example: fetch all cells in a range,
change their values and send an API request that update
cells in batch:

.. code:: python

   cell_list = worksheet.range('A1:C7')

   for cell in cell_list:
       cell.value = 'O_o'

   # Update in batch
   worksheet.update_cells(cell_list)
