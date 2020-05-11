API Reference
=============

.. module:: gspread

Top level
---------

.. autofunction:: oauth
.. autofunction:: service_account
.. autofunction:: authorize

Client
------

.. autoclass:: gspread.Client
   :members:

Models
------

The models represent common spreadsheet entities: :class:`a spreadsheet <gspread.models.Spreadsheet>`,
:class:`a worksheet <gspread.models.Worksheet>` and :class:`a cell <gspread.models.Cell>`.

.. note::

   The classes described below should not be instantiated by the end-user. Their
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
   :members: rowcol_to_a1, a1_to_rowcol, a1_range_to_grid_range,
             cast_to_a1_notation, absolute_range_name, is_scalar,
             filter_dict_values, accepted_kwargs

Auth
----

.. automodule:: gspread.auth
   :members: local_server_flow, console_flow

Exceptions
----------

.. autoexception:: gspread.exceptions.GSpreadException
.. autoexception:: gspread.exceptions.APIError

.. _github issue: https://github.com/burnash/gspread/issues
