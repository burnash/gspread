# Contributing Guide

* Check the [GitHub Issues](https://github.com/burnash/gspread/issues) for open issues that need attention.
* Follow the [How to submit a contribution](https://opensource.guide/how-to-contribute/#how-to-submit-a-contribution) Guide.

* Make sure unit tests pass. Please read how to run unit tests below.

* If you are fixing a bug:
  * If you are resolving an existing issue, reference the issue id in a commit message `(fixed #XXX)`.
  * If the issue has not been reported, please add a detailed description of the bug in the PR.
  * Please add a regression test case.

* If you are adding a new feature:
  * Please open a suggestion issue first.
  * Provide a convincing reason to add this feature and have it greenlighted before working on it.
  * Add tests to cover the functionality.

* Please follow [Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).

## Testing

1. [Obtain OAuth2 credentials from Google Developers Console](http://gspread.readthedocs.org/en/latest/oauth2.html)

2. Run tests offline:

Run the test suite using your current python version, in offline mode.
This will use the curently recorded HTTP requests + responses. It does not make any HTTP call, does not require an active internet connection.

```
tox -e py
```

**Tip:** To run a specific test method use the option `-k` to specifcy a test name and `-v` and `-s` to get test output on console.

Example:

```
pytest -v -s -k "test_find" tests/
```

**Note:** gspread uses [vcrpy](https://github.com/kevin1024/vcrpy) to record and replay HTTP interactions with Sheets API.

You must in that case provide a service account credentials in order to make the real HTTP requests, using `GS_CREDS_FILENAME` environment variable.

You can control vcrpy's [Record Mode](https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes) using `GS_RECORD_MODE` environment variable:

```
GS_RECORD_MODE=all GS_CREDS_FILENAME=<YOUR_CREDS.json> tox -e py
```

## Render Documentation

The documentation uses [reStructuredText](http://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html#rst-index) markup and is rendered by [Sphinx](http://www.sphinx-doc.org/).

To build the documentation locally, install Sphinx:

```
pip install Sphinx
```

Then from the project directory, run:

```
sphinx-build -b html docs html
```

Once finished, the rendered documentation will be in `html` folder. `index.html` is an entry point.
