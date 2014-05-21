.. gspread documentation master file, created by
   sphinx-quickstart on Thu Dec 15 14:44:32 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

gspread API Reference
=====================

`gspread <https://github.com/burnash/gspread>`_ is a simple `Google Spreadsheets`_ API wrapper.

.. _Google Spreadsheets: http://www.google.com/drive/apps.html

.. module:: gspread

.. contents:: :local:

Main Interface
--------------

.. autofunction:: login

.. autofunction:: authorize

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
.. autoexception:: WorksheetNotFound
.. autoexception:: NoValidUrlKeyFound
.. autoexception:: UpdateCellError
.. autoexception:: RequestError

Internal Modules
----------------

Following modules are for internal use only.

.. automodule:: gspread.httpsession
   :members: HTTPSession
.. automodule:: gspread.urls
   :members: construct_url

.. _github issue: https://github.com/burnash/gspread/issues

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

