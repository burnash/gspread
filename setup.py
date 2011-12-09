#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='gspread',
    description='Google Spreadsheets Python library',
    version='0.0.1',
    author='burnash',
    url='https://github.com/burnash/gspread',
    packages=['gspread'],
    license='MIT'
    )
