# Contributing Guide

- Check the [GitHub Issues](https://github.com/burnash/gspread/issues) for open issues that need attention.
- Follow the [How to submit a contribution](https://opensource.guide/how-to-contribute/#how-to-submit-a-contribution) Guide.

- Make sure unit tests pass. Please read how to run unit tests [below](#run-tests-offline).

- If you are fixing a bug:
  - If you are resolving an existing issue, reference the issue ID in a commit message `(e.g., fixed #XXXX)`.
  - If the issue has not been reported, please add a detailed description of the bug in the Pull Request (PR).
  - Please add a regression test case to check the bug is fixed.

- If you are adding a new feature:
  - Please open a suggestion issue first.
  - Provide a convincing reason to add this feature and have it greenlighted before working on it.
  - Add tests to cover the functionality.

- Please follow [Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).

## Tests

To run tests, add your credentials to `tests/creds.json` and run

```bash
GS_CREDS_FILENAME="tests/creds.json" GS_RECORD_MODE="all" tox -e py -- -k "<specific test to run>" -v -s
```

For more information on tests, see below.

## CI checks

If the [test](#run-tests-offline) or [lint](#lint) commands fail, the CI will fail, and you won't be able to merge your changes into gspread.

Use [format](#format) to format your code before submitting a PR. Not doing so may cause [lint](#lint) to fail.

## Install dependencies

```bash
pip install tox
```

## Run tests (offline)

If the calls to the Sheets API have not changed, you can run the tests offline. Otherwise, you will have to [run them online](#run-tests-online) to record the new API calls.

This will use the currently recorded HTTP requests + responses. It does not make any HTTP calls, and does not require an active internet connection.

```bash
tox -e py
```

### Run a specific test

```bash
tox -e py -- -k TEST_NAME -v -s
```

## Format

```bash
tox -e format
```

## Lint

```bash
tox -e lint
```

## Render Documentation

The documentation uses [reStructuredText](http://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html#rst-index) markup and is rendered by [Sphinx](http://www.sphinx-doc.org/).

```bash
tox -e doc
```

The rendered documentation is placed into `docs/build/html`. `index.html` is an entry point.

## Run tests (online)

gspread uses [vcrpy](https://github.com/kevin1024/vcrpy) to record and replay HTTP interactions with Sheets API.

### `GS_CREDS_FILENAME` environment variable

You must provide service account credentials using the `GS_CREDS_FILENAME` environment variable in order to make HTTP requests to the Sheets API.

[Obtain service account credentials from Google Developers Console](https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account).

### `GS_RECORD_MODE` environment variable

You can control vcrpy's [Record Mode](https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes) using `GS_RECORD_MODE` environment variable. It can be:

- `all` - record all HTTP requests, overwriting existing ones
- `new_episodes` - record new HTTP requests and replay existing ones
- `none` - replay existing HTTP requests only

In the following cases, you must record new HTTP requests:

- a new test is added
- an existing test is updated and does a new HTTP request
- gspread is updated and does a new HTTP request

### Run test, capturing *all* HTTP requests

In some cases if the test suite can't record new episodes, or it can't replay them offline, you can run a complete update of the cassettes.

```bash
GS_CREDS_FILENAME=<./YOUR_CREDS.json> GS_RECORD_MODE=all tox -e py
```

### Run test, capturing *only new* HTTP requests

To record new HTTP requests:

1. Remove the file holding the recorded HTTP requests of the test(s).
  e.g.,
     1. for the file `tests/cell_test.py`:
     2. for the test `test_a1_value`
     3. remove the file `tests/cassettes/CellTest.test_a1_value.json`
1. Run the tests with `GS_RECORD_MODE=new_episodes`.

```bash
GS_CREDS_FILENAME=<./YOUR_CREDS.json> GS_RECORD_MODE=new_episodes tox -e py
```

This will mostly result in a lot of updated files in `tests/cassettes/`. Don't forget to add them in your PR.
Please add them in a dedicated commit, in order to make the review process easier.

Afterwards, remember to [run the tests in offline mode](#run-tests-offline) to make sure you have recorded everything correctly.

## Release

Old release notes are [here](https://gist.github.com/burnash/335f977a74b8bfdc7968).

New release system:

- Update version number in [`gspread/__init__.py`](../gspread/__init__.py).
- Get changelog from drafting a new [GitHub release](https://github.com/burnash/gspread/releases/new) (do not publish, instead cancel.)
- Add changelog to [`HISTORY.rst`](../HISTORY.rst).
- Commit the changes as `Release vX.Y.Z` (do not push yet.)
- Run `tox -e lint,py,build,doc` to check build/etc.
- Push the commit. Wait for the CI to pass.
- Add a tag `vX.Y.Z` to the commit locally. This will trigger a new release on PyPi, and make a release on GitHub.
- View the release on [GitHub](https://github.com/burnash/gspread/releases) and [PyPi](https://pypi.org/project/gspread/)!
