API Reference
=============

.. module:: gspread

Top level
---------

.. autofunction:: authorize

Client
------

.. autoclass:: gspread.Client
   :members:

Models
------

The models represent common spreadsheet objects: :class:`a spreadsheet <Spreadsheet>`,
:class:`a worksheet <Worksheet>` and :class:`a cell <Cell>`.

.. note::

   The classes described below should not be instantiated by end-user. Their
   instances result from calling other objects' methods.

.. autoclass:: gspread.models.Spreadsheet
   :members:
.. autoclass:: gspread.models.Worksheet
   :members:
.. autoclass:: gspread.models.Cell
   :members:

Utils
-----

.. automodule:: gspread.utils
   :members: rowcol_to_a1, a1_to_rowcol

Exceptions
----------

.. autoexception:: gspread.exceptions.GSpreadException
.. autoexception:: gspread.exceptions.APIError

.. _github issue: https://github.com/burnash/gspread/issues
