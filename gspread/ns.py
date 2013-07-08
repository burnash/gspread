# -*- coding: utf-8 -*-

"""
gspread.ns
~~~~~~~~~~

This module contains namespaces used across the project and related
helper functions.

"""

ATOM_NS = 'http://www.w3.org/2005/Atom'
SPREADSHEET_NS = 'http://schemas.google.com/spreadsheets/2006'
BATCH_NS = 'http://schemas.google.com/gdata/batch'


def _ns(name):
    return '{%s}%s' % (ATOM_NS, name)


def _ns1(name):
    return '{%s}%s' % (SPREADSHEET_NS, name)
