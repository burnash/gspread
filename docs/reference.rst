API Reference
=============

.. module:: gspread

.. contents:: :local:

Main interface
--------------

.. autofunction:: login

.. autoclass:: Client
   :members:

Models
------

The models represent common spreadsheet objects: :class:`a spreadsheet <Spreadsheet>`,
:class:`a worksheet <Worksheet>` and :class:`a cell <Cell>`.

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

Internal modules
----------------

Following modules are for internal use only.

.. automodule:: gspread.httpsession
   :members: HTTPSession
.. automodule:: gspread.urls
   :members: construct_url
