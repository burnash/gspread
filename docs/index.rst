gspread
=======

`gspread`_ is a Python API for Google Sheets.

Features:

-  Google Sheets API v4.
-  Open a spreadsheet by title, key or url.
-  Read, write, and format cell ranges.
-  Sharing and access control.
-  Batching updates.


Installation
------------

.. code:: sh

   pip install gspread


Requirements: Python 2.7+ or Python 3+.


Quick Example
-------------

.. code:: python

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


Getting Started
---------------

.. toctree::
   :maxdepth: 2

   oauth2


Usage
-----

.. toctree::
    :maxdepth: 2

    user-guide

Advanced
--------

.. toctree::
    :maxdepth: 2

    advanced


API Documentation
---------------------------

.. toctree::
   :maxdepth: 2

   api


How to Contribute
-----------------

Please make sure to take a moment and read the `Code of Conduct`_.

Ask Questions
~~~~~~~~~~~~~

The best way to get an answer to a question is to ask on `Stack Overflow
with a gspread tag`_.

Report Issues
~~~~~~~~~~~~~

Please report bugs and suggest features via the `GitHub Issues`_.

Before opening an issue, search the tracker for possible duplicates. If
you find a duplicate, please add a comment saying that you encountered
the problem as well.

Contribute code
~~~~~~~~~~~~~~~

Please make sure to read the `Contributing Guide`_ before making a pull
request.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _gspread: https://github.com/burnash/gspread
.. _Obtain OAuth2 credentials from Google Developers Console: oauth2.html
.. _Code of Conduct: https://github.com/burnash/gspread/blob/master/.github/CODE_OF_CONDUCT.md
.. _Stack Overflow with a gspread tag: http://stackoverflow.com/questions/tagged/gspread?sort=votes&pageSize=50
.. _GitHub Issues: https://github.com/burnash/gspread/issues
.. _Contributing Guide: https://github.com/burnash/gspread/blob/master/.github/CONTRIBUTING.md
