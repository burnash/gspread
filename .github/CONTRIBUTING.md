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

1. Go to Google Sheets and create an empty spreadsheet you will use for testing.
2. Create a configuration file from config dummy:

    ```sh
    cp tests/tests.config.example tests/tests.config
    ```

3. Open `tests.config` with an editor and fill up config parameters with your testing spreadsheet's info.
4. Install [Nose](http://nose.readthedocs.org).
5. Download credentials json file(see [doc](http://gspread.readthedocs.io/en/latest/oauth2.html#using-signed-credentials)),
rename it to `creds.json` and put it into the tests folder.
6. Run tests:

    ```sh
    nosetests
    ```
