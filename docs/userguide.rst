User Guide
==========

Installation
------------

There are two options for installing *gspread*. The library is in active
development now, so the recommended way is to check out the source from 
GitHub and to pull new updates from time to time.

From GitHub
^^^^^^^^^^^
::

    git clone https://github.com/burnash/gspread.git
    cd gspread
    python setup.py install

To get updates::
    
    cd gspread
    git pull
    python setup.py install

From Pypi
^^^^^^^^^

The alternative way is to install from the Python Package Index::

    pip install gspread --upgrade

And if you're on easy_install, it's::

    easy_install -U gspread


Quickstart
----------

Signing In
^^^^^^^^^^
To start working with your Google spreadsheets you need to sign in 
to the service. This can be done with your Google Account::

    gc = gspread.login('account@gmail.com','password')

Openning A Spreadsheet
^^^^^^^^^^^^^^^^^^^^^^

One of the main features of `gspread` is the ability to easily open 
a spreadsheet by its title. Assuming you have a spreadsheet named 
"Annual report" in list of your Google Docs, you can do following 
to open it up in your Python code::

    spreadsheet = gc.open("Annual report")

Pretty easy. However, Google Docs allows you to have more than one
spreadsheet under the same name. What will happen in this case?
Well, in this case the :meth:`~gspread.Client.open` method will return 
the first spreadsheet it finds with this name. This is a rare case, since
you really don't want to have many documents with the same name.

For those who want to be totally specific while opening a document other
methods exist. First one is to use unique key assigned to every 
Google Docs document. You can see it in the browser's address bar 
when you working with your spreadsheet::

    https://docs.google.com/spreadsheet/ccc?key=1AkgN6IO_5rdrprh0V1pQVjFlQ2mIUDd3VTZ3ZjJubWc#gid=0

In this case the key is ``0AkgM6iO_6dprdHF0V1pQVjFlQ2FIUDd0VTZ3ZjJubWc``. 
And the code to use to open this spreadsheet will be::

    spreadsheet = gc.open_by_key('0AkgM6iO_6dprdHF0V1pQVjFlQ2FIUDd0VTZ3ZjJubWc')

If you're somewhat lazy person (like I am), you can copy the entire 
spreadsheet's url from address bar and paste it into another useful 
method, called :meth:`~gspread.Client.open_by_url`::
    
    spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheet/ccc?key=1AkgN6IO_5rdrprh0V1pQVjFlQ2mIUDd3VTZ3ZjJubWc#gid=0")


Selecting A Worksheet
^^^^^^^^^^^^^^^^^^^^^

Each `spreadsheet` consists of one or many `worksheets` (also called `sheets`). This is a next step
in container hierarchy. Worksheets can be selected by title or index. 
In my point of view, the greatest percentage of spreadsheets have
only one worksheet (called *Sheet1* by default). For this common case
:class:`~gspread.Spreadsheet` object got a handy shortcut property :attr:`~gspread.Spreadsheet.sheet1`.
