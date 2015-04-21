Release History
===============

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
