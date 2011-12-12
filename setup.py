#!/usr/bin/env python

import gspread

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='gspread',
    packages=['gspread'],
    description='Google Spreadsheets Python library',
    version=gspread.__version__,
    author='Anton Burnashev',
    author_email='fuss.here@gmail.com',
    url='https://github.com/burnash/gspread',
    keywords=['spreadsheets', 'google-spreadsheets'],
    classifiers=[
        "Programming Language :: Python",
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
