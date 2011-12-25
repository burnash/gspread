#!/usr/bin/env python

import os.path
import gspread

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

description = 'Google Spreadsheets Python library'

long_description = """
{index}

License
-------
MIT

Download
========
"""

long_description = long_description.lstrip("\n").format(index=read('docs/index.txt'))

setup(
    name='gspread',
    packages=['gspread'],
    description=description,
    long_description=long_description,
    version=gspread.__version__,
    author='Anton Burnashev',
    author_email='fuss.here@gmail.com',
    url='https://github.com/burnash/gspread',
    keywords=['spreadsheets', 'google-spreadsheets'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
    license='MIT'
    )
