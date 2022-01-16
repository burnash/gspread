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

**Note:** the CI runs that command, if it fail you won't be able to merge
your changes in GSpread.

```
tox -e py
```

**Tip:** To run a specific test method use the option `-k` to specifcy a test name and `-v` and `-s` to get test's output on console.

Example:

```
tox -e py -- -k test_find -v -s
```

**Note:** gspread uses [vcrpy](https://github.com/kevin1024/vcrpy) to record and replay HTTP interactions with Sheets API.

You must in that case provide a service account credentials in order to make the real HTTP requests, using `GS_CREDS_FILENAME` environment variable.

You can control vcrpy's [Record Mode](https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes) using `GS_RECORD_MODE` environment variable.

The following command will run the entire test suite and record every HTTP request.
```
GS_RECORD_MODE=all GS_CREDS_FILENAME=<YOUR_CREDS.json> tox -e py
```

You need to update the recorded HTTP requests in the following cases:

- new test is added
- a existing test is updated and does a new HTTP request
- gspread is updated and does a new HTTP request

In any of the above cases:

- remove the file holding the init/teardown of the test suite.

  ex: for the file `tests/cell_test.py` delete `tests/cassettes/CellTest.json`
- please update the HTTP recording using the command above
- set the `GS_RECORD_MODE` to `new_episodes`.

This will tell `vcrpy` to record only new episodes and replay existing episodes.

**Note:** this will mostly result in a lot of udpated files under `tests/cassettes/` don't forget to add them in your PR.

Add these new files a dedicated commit, in order to make the review process easier please.

The following command will replay existing requests and record new requests:
```
GS_RECORD_MODE=new_episodes GS_CREDS_FILENAME=<YOUR_CREDS.json> tox -e py
```

Then run the tests in offline mode to make sure you have recorded everything.

```
tox -e py
```

**Note::** In some cases if the test suite can't record new episodes or it can't
replay them offline, you can run a complete update of the cassettes using the following command:

```
GS_RECORD_MODE=all GS_CREDS_FILENAME=<YOUR_CREDS.json> tox -e py
```

3. Format your code:

Use the following command to format your code. Doing so will ensure
all code respects the same format.

```
tox -e format
```

Then run the linter to validate change, if any.

**Note:** the CI runs that command, if it fail you won't be able to merge
your changes in GSpread.

```
tox -e lint
```

## Render Documentation

The documentation uses [reStructuredText](http://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html#rst-index) markup and is rendered by [Sphinx](http://www.sphinx-doc.org/).

To build the documentation locally, use the following command:

```
tox -e doc
```

Once finished, the rendered documentation will be in `docs/build/html` folder. `index.html` is an entry point.
