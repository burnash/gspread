API Reference
=============

.. module:: gspread

Main interface
--------------

.. autoclass:: Client
   :members:

Models
------

The models represent common spreadsheet objects: a spreadsheet, a worksheet and a cell.

.. note::

   The classes described below should not be instantiated by end-user. Their
   instances result from calling other objects' methods.

.. autoclass:: Spreadsheet
   :members:
.. autoclass:: Worksheet
   :members:
.. autoclass:: Cell
   :members:

Exceptions
----------

.. autoexception:: GSpreadException
.. autoexception:: AuthenticationError
.. autoexception:: SpreadsheetNotFound
.. autoexception:: NoValidUrlKeyFound
