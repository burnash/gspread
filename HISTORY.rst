Release History
===============

<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
0.5.0 (2016-12-12)
------------------

* Added method to create blank spreadsheets #253
* Added method to clear worksheets #156
* Added method to delete a row in a worksheet #337
* Changed `Worksheet.range` method to accept integers as coordinates #142
* Added `default_blank` parameter to `Worksheet.get_all_records` #423
* Use xml.etree.cElementTree when available to reduce memory usage #348
* Fixed losing input_value data from following cells in `Worksheet.insert_row` #338
* Deprecated `Worksheet.get_int_addr` and `Worksheet.get_addr_int`
  in favour of `utils.a1_to_rowcol` and `utils.rowcol_to_a1` respectively


0.4.1 (2016-07-17)
------------------

* Fix exception format to support Python 2.6


=======
<<<<<<< HEAD
>>>>>>> Update README.md
0.4.0 (2016-06-30)
------------------

* Use request session's connection pool in HTTPSession

* Removed deprecated ClientLogin


=======
<<<<<<< HEAD
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
>>>>>>> # This is a combination of 2 commits.
=======
>>>>>>> Update README.md
>>>>>>> Update README.md
0.3.0 (2015-12-15)
------------------

* Use Python requests instead of the native HTTPConnection object

* Optimized row_values and col_values

* Optimized row_values and col_values
  Removed the _fetch_cells call for each method. This eliminates the
  adverse effect on runtime for large worksheets.

  Fixes #285, #190, #179, and #113

* Optimized row_values and col_values
  Removed the _fetch_cells call for each method. This eliminates the
  adverse effect on runtime for large worksheets.

  Fixes #285, #190, #179, and #113

* Altered insert_row semantics to utilize range
  This avoids issuing one API request per cell to retrieve the Cell
  objects after the insertion row. This provides a significant speed-up
  for insertions at the beginning of large sheets.

* Added mock tests for Travis (MockSpreadsheetTest)

* Fixed XML header issue with Python 3

* Fixed Worksheet.export function and associated test

* Added spreadsheet feed helper

* Add CellNotFound to module exports
  Fixes #88

* Fixed utf8 encoding error caused by duplicate XML declarations
* Fixed AttributeError when URLError caught by HTTPError catch block
  Fixes #257

* Added __iter__ method to Spreadsheet class

* Fixed export test
* Switched tests to oauth

<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
=======
=======
>>>>>>> # This is a combination of 2 commits.
>>>>>>> Update README.md
>>>>>>> Update README.md
0.2.5 (2015-04-22)
------------------

* Deprecation warning for ClientLogin #210
* Redirect github pages to ReadTheDocs
* Bugfixes

0.2.4 (2015-04-17)
------------------

* Output error response #219 #170 #194.
* Added instructions on how to get oAuth credentials to docs.

0.2.3 (2015-03-11)
------------------

* Fixed issue with `Spreadsheet.del_worksheet`.
* Automatically refresh OAuth2 token when it has expired.
* Added an `insert_row` method to `Worksheet`.
* Moved docs to Read The Docs.
* Added the `numeric_value` attribute to `Cell`.
* Added title property to `Spreadsheet`.
* Support for exporting worksheets.
* Added row selection for keys in `Worksheet.get_all_records`.

0.2.2 (2014-08-26)
------------------

* Fixed version not available for read-only spreadsheets bug

0.2.1 (2014-05-10)
------------------

* Added OAuth2 support
* Fixed regression bug #130. Not every POST needs If-Match header

0.2.0 (2014-05-09)
------------------

* New Google Sheets support.
* Fixed get_all_values() on empty worksheet.
* Bugfix in get_int_addr().
* Changed the HTTP connectivity from urllib to httlib for persistent http connections.

0.1.0 (2013-07-09)
------------------

* Support for deleting worksheets from a spreadsheet.

0.0.15 (2013-02-01)
------------------

* Couple of bugfixes.

0.0.14 (2013-01-31)
------------------

* Bugfix in Python 3.


0.0.12 (2011-12-25)
------------------

* Python 3 support.


0.0.9 (2011-12-16)
------------------

* Enter the Docs.
* New skinnier login method.


0.0.7 (2011-12-14)
------------------

* Pypi install bugfix.


0.0.6 (2011-12-13)
------------------

* Batch cells update.


0.0.2 (2011-12-12)
------------------

* New spreadsheet open methods:

    - Client.open_by_key
    - Client.open_by_url


0.0.1 (2011-12-12)
------------------

* Got rid of the wrapper.
* Support for pluggable http session object.


pre 0.0.1 (2011-12-02)
----------------------

* Hacked a wrapper around Google's Python client library.
