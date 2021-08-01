#!/usr/bin/env python

import os.path
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    sys.exit()


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


description = 'Google Spreadsheets Python API'

long_description = """
{index}

License
-------
MIT
"""

long_description = long_description.lstrip("\n").format(index=read('docs/index.txt'))

version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                    read('gspread/__init__.py'), re.MULTILINE).group(1)

setup(
    name='gspread',
    packages=['gspread'],
    description=description,
    long_description=long_description,
    version=version,
    author='Anton Burnashev',
    author_email='fuss.here@gmail.com',
    url='https://github.com/burnash/gspread',
    keywords=['spreadsheets', 'google-spreadsheets'],
    install_requires=[
        'google-auth>=1.12.0',
        'google-auth-oauthlib>=0.4.1'
    ],
    python_requires='>=3.4, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
    license='MIT'
    )
