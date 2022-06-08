#!/usr/bin/env python

import os
import re
import sys
from pathlib import Path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel")
    sys.exit()


def file_content(filename):
    return Path(filename).read_text(encoding="utf-8")


description = "Google Spreadsheets Python API"

long_description = """
{index}

License
-------
MIT
"""

long_description = long_description.lstrip("\n").format(
    index=file_content("docs/index.txt")
)
version = re.search(
    r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    file_content("gspread/__init__.py"),
    re.MULTILINE,
).group(1)


setup(
    name="gspread",
    packages=["gspread"],
    description=description,
    long_description=long_description,
    version=version,
    author="Anton Burnashev",
    author_email="fuss.here@gmail.com",
    maintainer="Alexandre Lavigne",
    maintainer_email="lavigne958@gmail.com",
    url="https://github.com/burnash/gspread",
    keywords=["spreadsheets", "google-spreadsheets"],
    install_requires=["google-auth>=1.12.0", "google-auth-oauthlib>=0.4.1"],
    python_requires=">=3.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="MIT",
)
