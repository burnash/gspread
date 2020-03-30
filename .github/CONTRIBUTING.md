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
2. Install test requirements:

```
pip install -r test-requirements.txt
```

3. Run tests:

```
GS_CREDS_FILENAME=<YOUR_CREDS.json> nosetests -vv tests/test.py
```

where `YOUR_CREDS.json` is a path to the file you downloaded in step 1.

**Tip:** To run a specific test method append its name in the form of `:TestClassName.test_method_name` to `tests/test.py`. 

Example:

```
GS_CREDS_FILENAME=<YOUR_CREDS.json> nosetests -vv tests/test.py:WorksheetTest.test_find
```

**Note:** gspread uses [Betamax](https://github.com/betamaxpy/betamax) to record and replay HTTP interactions with Sheets API.
You can control Betamax's [Record Mode](https://betamax.readthedocs.io/en/latest/record_modes.html) using `GS_RECORD_MODE` environment variable:

```
GS_RECORD_MODE=all GS_CREDS_FILENAME=<YOUR_CREDS.json> nosetests -vv tests/test.py
```

