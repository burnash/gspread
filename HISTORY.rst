Release History
===============

6.2.0 (2025-02-27)
------------------

* Add property expiry in gspread client by @lavigne958 in https://github.com/burnash/gspread/pull/1453
* Bump typing-extensions from 4.11.0 to 4.12.0 by @dependabot in https://github.com/burnash/gspread/pull/1471
* Fix code block formatting typo in README by @agrvz in https://github.com/burnash/gspread/pull/1474
* ignore jinja CVE by @lavigne958 in https://github.com/burnash/gspread/pull/1481
* Type part of test suite utils by @lavigne958 in https://github.com/burnash/gspread/pull/1483
* Remove passing exception as args to super in APIError by @mike-flowers-airbnb in https://github.com/burnash/gspread/pull/1477
* Bump mypy from 1.10.0 to 1.10.1 by @dependabot in https://github.com/burnash/gspread/pull/1488
* Update advanced.rst by @yatender-rjliving in https://github.com/burnash/gspread/pull/1492
* Bump bandit from 1.7.8 to 1.7.9 by @dependabot in https://github.com/burnash/gspread/pull/1485
* Bump flake8 from 7.0.0 to 7.1.0 by @dependabot in https://github.com/burnash/gspread/pull/1486
* Bump typing-extensions from 4.12.0 to 4.12.2 by @dependabot in https://github.com/burnash/gspread/pull/1480
* Bump mypy from 1.10.1 to 1.11.1 by @dependabot in https://github.com/burnash/gspread/pull/1497
* Bump black from 24.4.2 to 24.8.0 by @dependabot in https://github.com/burnash/gspread/pull/1499
* Bump flake8 from 7.1.0 to 7.1.1 by @dependabot in https://github.com/burnash/gspread/pull/1501
* Fix docstring about BackOffHTTPClient by @pataiji in https://github.com/burnash/gspread/pull/1502
* Fix comment to reflect correct google-auth package version requirement by @ikmals in https://github.com/burnash/gspread/pull/1503
* Doc/community addons orm package by @lavigne958 in https://github.com/burnash/gspread/pull/1506
* fix: fix type annotation for default_blank by @hiro-o918 in https://github.com/burnash/gspread/pull/1505
* Bump mypy from 1.11.1 to 1.11.2 by @dependabot in https://github.com/burnash/gspread/pull/1508
* better handler API error parsing. by @lavigne958 in https://github.com/burnash/gspread/pull/1510
* Add test on receiving an invalid JSON in the APIError exception handler. by @lavigne958 in https://github.com/burnash/gspread/pull/1512
* [feature] Add 'expand_table' feature by @lavigne958 in https://github.com/burnash/gspread/pull/1475
* Bump bandit from 1.7.9 to 1.7.10 by @dependabot in https://github.com/burnash/gspread/pull/1514
* Created a `batch_merge` function [Issue #1473] by @muddi900 in https://github.com/burnash/gspread/pull/1498
* Added a range option to `Worksheet.get_notes` [Issue #1482] by @muddi900 in https://github.com/burnash/gspread/pull/1487
* Documentation update for gspread.worksheet.Worksheet.get_all_records by @levon003 in https://github.com/burnash/gspread/pull/1529
* add example for `batch_merge` by @alifeee in https://github.com/burnash/gspread/pull/1542
* explicitly list exported package symbols by @alinsavix in https://github.com/burnash/gspread/pull/1531

6.1.4 (2024-10-21)
------------------

* remove dependency on requests-2.27.0

6.1.3 (2024-10-03)
------------------

* ignore jinja CVE by @lavigne958 in https://github.com/burnash/gspread/pull/1481
* Remove passing exception as args to super in APIError by @mike-flowers-airbnb in https://github.com/burnash/gspread/pull/1477
* better handler API error parsing. by @lavigne958 in https://github.com/burnash/gspread/pull/1510
* Add test on receiving an invalid JSON in the APIError exception handler. by @lavigne958 in https://github.com/burnash/gspread/pull/1512

6.1.2 (2024-05-17)
------------------

* add note about runnings tests to contrib guide by @alifeee in https://github.com/burnash/gspread/pull/1465
* Some updates on `get_notes` by @nbwzx in https://github.com/burnash/gspread/pull/1461

6.1.1 (2024-05-16)
------------------

* Add some missing typing in code by @lavigne958 in https://github.com/burnash/gspread/pull/1448
* More fixes for `Worksheet.update` argument ordering & single cell updating (i.e. now `Worksheet.update_acell`) by @alexmalins in https://github.com/burnash/gspread/pull/1449
* Added 'add_data_validation` to `Workhsheet` [Issue #1420] by @muddi900 in https://github.com/burnash/gspread/pull/1444
* Bump typing-extensions from 4.10.0 to 4.11.0 by @dependabot in https://github.com/burnash/gspread/pull/1450
* Bump black from 23.3.0 to 24.4.0 by @dependabot in https://github.com/burnash/gspread/pull/1452
* Fix incorrect version number in HISTORY.rst from 6.0.1 to 6.1.0 by @yhay81 in https://github.com/burnash/gspread/pull/1455
* add `get_notes` by @nbwzx in https://github.com/burnash/gspread/pull/1451
* Bump mypy from 1.9.0 to 1.10.0 by @dependabot in https://github.com/burnash/gspread/pull/1459
* Bump black from 24.4.0 to 24.4.2 by @dependabot in https://github.com/burnash/gspread/pull/1460
* bugfix: handle domain name in spreadsheet copy permissions by @lavigne958 in https://github.com/burnash/gspread/pull/1458
* Fix/api key auth version by @alifeee in https://github.com/burnash/gspread/pull/1463
* Ignore pip vulnerabilities in CI. by @lavigne958 in https://github.com/burnash/gspread/pull/1464
* Remove StrEnum dependency and added custom class[issue #1462] by @muddi900 in https://github.com/burnash/gspread/pull/1469

6.1.0 (2024-03-28)
------------------

* Add py.typed marker by @lavigne958 in https://github.com/burnash/gspread/pull/1422
* Improve back-off client by @lavigne958 in https://github.com/burnash/gspread/pull/1415
* Add new auth method API key by @lavigne958 in https://github.com/burnash/gspread/pull/1428
* Bugfix/add set timeout by @lavigne958 in https://github.com/burnash/gspread/pull/1417
* Fix wrapper `cast_to_a1_notation` by @lavigne958 in https://github.com/burnash/gspread/pull/1427
* Bump bandit from 1.7.5 to 1.7.8 by @dependabot in https://github.com/burnash/gspread/pull/1433
* Bump mypy from 1.6.1 to 1.9.0 by @dependabot in https://github.com/burnash/gspread/pull/1432
* Bump typing-extensions from 4.8.0 to 4.10.0 by @dependabot in https://github.com/burnash/gspread/pull/1424
* Bump flake8 from 5.0.4 to 7.0.0 by @dependabot in https://github.com/burnash/gspread/pull/1375
* fix error message readability by @imrehg in https://github.com/burnash/gspread/pull/1435
* Add missing method `import_csv()` by @lavigne958 in https://github.com/burnash/gspread/pull/1426
* update readme examples by @alifeee in https://github.com/burnash/gspread/pull/1431
* Add user friendly message when we can't override a test cassette by @lavigne958 in https://github.com/burnash/gspread/pull/1438
* Allow "warning" type protected ranges by @alifeee in https://github.com/burnash/gspread/pull/1439
* Improve README and documentation with value render options by @lavigne958 in https://github.com/burnash/gspread/pull/1446

6.0.2 (2024-02-14)
------------------

* Fixup gspread client init arguments by @lavigne958 in https://github.com/burnash/gspread/pull/1412

6.0.1 (2024-02-06)
------------------

* Allow client to use external Session object by @lavigne958 in https://github.com/burnash/gspread/pull/1384
* Remove-py-3.7-support by @alifeee in https://github.com/burnash/gspread/pull/1396
* bugfix/client export by @lavigne958 in https://github.com/burnash/gspread/pull/1392
* Fix oauth flow typo by @alifeee in https://github.com/burnash/gspread/pull/1397
* check oauth creds type using `isinstance` by @alifeee in https://github.com/burnash/gspread/pull/1398
* Fix type hints at find method in worksheet.py by @deftfitf in https://github.com/burnash/gspread/pull/1407
* Fixup get empty cell value is `None` by @lavigne958 in https://github.com/burnash/gspread/pull/1404
* Fix missing attribute `spreadsheet` in `Worksheet`. by @lavigne958 in https://github.com/burnash/gspread/pull/1402
* update migration guide by @alifeee in https://github.com/burnash/gspread/pull/1409

6.0.0 (2024-01-28)
------------------
New Contributor
* Remove deprecated method delete_row by @cgkoutzigiannis in https://github.com/burnash/gspread/pull/1062
* Initial typing in client.py by @OskarBrzeski in https://github.com/burnash/gspread/pull/1159
* Split client http client by @lavigne958 in https://github.com/burnash/gspread/pull/1190
* Spelling fix & update docs with date_time_render_option behaviour by @alifeee in https://github.com/burnash/gspread/pull/1187
* #966  Add sketch typing for utils.py by @butvinm in https://github.com/burnash/gspread/pull/1196
* Remove accepted_kwargs decorator by @lavigne958 in https://github.com/burnash/gspread/pull/1229
* Remove/python-3.7 by @alifeee in https://github.com/burnash/gspread/pull/1234
* Bump isort from 5.11.4 to 5.12.0 by @dependabot in https://github.com/burnash/gspread/pull/1165
* bump flake8 to 6.0.0 by @alifeee in https://github.com/burnash/gspread/pull/1236
* merge master into 6.0.0 by @lavigne958 in https://github.com/burnash/gspread/pull/1241
* Remplace named tuples with enums by @lavigne958 in https://github.com/burnash/gspread/pull/1250
* Feature/add type hints worksheets by @lavigne958 in https://github.com/burnash/gspread/pull/1254
* Implement hex color conversion by @idonec in https://github.com/burnash/gspread/pull/1270
* remove lastUpdateTime by @alifeee in https://github.com/burnash/gspread/pull/1295
* Merge `master` into `feature/release_6_0_0` by @alifeee in https://github.com/burnash/gspread/pull/1320
* Add type checking to lint by @alifeee in https://github.com/burnash/gspread/pull/1337
* Warning/update swapped args by @alifeee in https://github.com/burnash/gspread/pull/1336
* Improve `Worksheet.sort()` signature by @lavigne958 in https://github.com/burnash/gspread/pull/1342
* Make `get_values` and alias of `get` by @alifeee in https://github.com/burnash/gspread/pull/1296
* fix type issue (remove `.first()` function) by @alifeee in https://github.com/burnash/gspread/pull/1344
* Remove/get records   use index by @alifeee in https://github.com/burnash/gspread/pull/1345
* increase warning stacklevel from 1 to 2 by @alifeee in https://github.com/burnash/gspread/pull/1361
* Feature/merge master by @lavigne958 in https://github.com/burnash/gspread/pull/1371
* feature/merge master by @lavigne958 in https://github.com/burnash/gspread/pull/1372
* Simplify get records by @alifeee in https://github.com/burnash/gspread/pull/1374
* Add util function `to_records` to build records by @lavigne958 in https://github.com/burnash/gspread/pull/1377
* feature/add utils get records by @lavigne958 in https://github.com/burnash/gspread/pull/1378
* Add migration guide for get_all_records by @lavigne958 in https://github.com/burnash/gspread/pull/1379
* feature/merge master into release 6 0 0 by @lavigne958 in https://github.com/burnash/gspread/pull/1381
* Feature/release 6 0 0 by @lavigne958 in https://github.com/burnash/gspread/pull/1382

5.12.4 (2023-12-31)
-------------------

* Bump actions/setup-python from 4 to 5 by @dependabot in https://github.com/burnash/gspread/pull/1370
* Fixed default value of merge_type parameter in merge_cells function docstring. by @neolooong in https://github.com/burnash/gspread/pull/1373

5.12.3 (2023-12-15)
-------------------

* 1363 get all records retrieves a large number of empty rows after the end of the data by @alifeee in https://github.com/burnash/gspread/pull/1364

5.12.2 (2023-12-04)
-------------------

* Many fixes for `get_records` by @alifeee in https://github.com/burnash/gspread/pull/1357
* change `worksheet.update` migration guide by @alifeee in https://github.com/burnash/gspread/pull/1362

5.12.1 (2023-11-29)
-------------------

* feature/readme migration v6 by @lavigne958 in https://github.com/burnash/gspread/pull/1297
* add deprecation warnings for lastUpdateTime... by @alifeee in https://github.com/burnash/gspread/pull/1333
* remove `use_index` and references to it in `get_records` by @alifeee in https://github.com/burnash/gspread/pull/1343
* make deprecation warning dependent on if kwarg is used for client_factory by @alifeee in https://github.com/burnash/gspread/pull/1349
* fix 1352 expected headers broken by @alifeee in https://github.com/burnash/gspread/pull/1353
* fix `combine_merged_cells` when using from a range that doesn't start at `A1` by @alifeee in https://github.com/burnash/gspread/pull/1335

5.12.0 (2023-10-22)
-------------------

* feature -- adding `worksheet.get_records` to get specific row ranges by @AndrewBasem1 in https://github.com/burnash/gspread/pull/1301
* Fix list_spreadsheet_files return value by @mephinet in https://github.com/burnash/gspread/pull/1308
* Fix warning message for `worksheet.update` method by @ksj20 in https://github.com/burnash/gspread/pull/1312
* change lambda function to dict (fix pyupgrade issue) by @alifeee in https://github.com/burnash/gspread/pull/1319
* allows users to silence deprecation warnings by @lavigne958 in https://github.com/burnash/gspread/pull/1324
* Add `maintain_size` to keep asked for size in `get`, `get_values` by @alifeee in https://github.com/burnash/gspread/pull/1305

5.11.3 (2023-09-29)
-------------------

* Fix list_spreadsheet_files return value by @mephinet in https://github.com/burnash/gspread/pull/1308

5.11.2 (2023-09-18)
-------------------

* Fix merge_combined_cells in get_values (AND 5.11.2 RELEASE) by @alifeee in https://github.com/burnash/gspread/pull/1299

5.11.1 (2023-09-06)
-------------------

* Bump actions/checkout from 3 to 4 by @dependabot in https://github.com/burnash/gspread/pull/1288
* remove Drive API access on Spreadsheet init (FIX - VERSION 5.11.1) by @alifeee in https://github.com/burnash/gspread/pull/1291

5.11.0 (2023-09-04)
-------------------

* add docs/build to .gitignore by @alifeee in https://github.com/burnash/gspread/pull/1246
* add release process to CONTRIBUTING.md by @alifeee in https://github.com/burnash/gspread/pull/1247
* Update/clean readme badges by @lavigne958 in https://github.com/burnash/gspread/pull/1251
* add test_fill_gaps and docstring for fill_gaps by @alifeee in https://github.com/burnash/gspread/pull/1256
* Remove API calls from `creationTime`/`lastUpdateTime` by @alifeee in https://github.com/burnash/gspread/pull/1255
* Fix Worksheet ID Type Inconsistencies by @FlantasticDan in https://github.com/burnash/gspread/pull/1269
* Add `column_count` prop as well as `col_count` by @alifeee in https://github.com/burnash/gspread/pull/1274
* Add required kwargs with no default value by @lavigne958 in https://github.com/burnash/gspread/pull/1271
* Add deprecation warnings for colors by @alifeee in https://github.com/burnash/gspread/pull/1278
* Add better Exceptions on opening spreadsheets by @alifeee in https://github.com/burnash/gspread/pull/1277

5.10.0 (2023-06-29)
-------------------

* Fix rows_auto_resize in worksheet.py by removing redundant self by @MagicMc23 in https://github.com/burnash/gspread/pull/1194
* Add deprecation warning for future release 6.0.x by @lavigne958 in https://github.com/burnash/gspread/pull/1195
* FEATURE: show/hide gridlines (#1197) by @alifeee in https://github.com/burnash/gspread/pull/1202
* CLEANUP: cleanup tox.ini, and ignore ./env by @alifeee in https://github.com/burnash/gspread/pull/1200
* Refactor/update-contributing-guide by @alifeee in https://github.com/burnash/gspread/pull/1206
* Spelling fix (with legacy option) by @alifeee in https://github.com/burnash/gspread/pull/1210
* 457-fetch-without-hidden-worksheets by @alifeee in https://github.com/burnash/gspread/pull/1207
* Add_deprecated_warning_sort_method by @lavigne958 in https://github.com/burnash/gspread/pull/1198
* Update (and test for) internal properties on change by @alifeee in https://github.com/burnash/gspread/pull/1211
* Feature: Add "Remove tab colour" method by @alifeee in https://github.com/burnash/gspread/pull/1199
* Refresh-test-cassettes by @alifeee in https://github.com/burnash/gspread/pull/1217
* update self._properties after batch_update by @alifeee in https://github.com/burnash/gspread/pull/1221
* 700-fill-merged-cells by @alifeee in https://github.com/burnash/gspread/pull/1215
* Fix/update-internal-properties by @alifeee in https://github.com/burnash/gspread/pull/1225
* Add breaking change warning in Worksheet.update() by @lavigne958 in https://github.com/burnash/gspread/pull/1226
* Bump codespell from 2.2.4 to 2.2.5 by @dependabot in https://github.com/burnash/gspread/pull/1232
* Add/refresh last update time by @alifeee in https://github.com/burnash/gspread/pull/1233
* Update-build-tools by @alifeee in https://github.com/burnash/gspread/pull/1231
* add read the doc configuration file by @lavigne958 in https://github.com/burnash/gspread/pull/1235
* update licence year by @alifeee in https://github.com/burnash/gspread/pull/1237
* remove deprecated methods from tests by @alifeee in https://github.com/burnash/gspread/pull/1238

5.9.0 (2023-05-11)
------------------

* Bugfix/fix get last update time by @lavigne958 in https://github.com/burnash/gspread/pull/1186
* Add batch notes insert/update/clear by @lavigne958 in https://github.com/burnash/gspread/pull/1189

5.8.0 (2023-04-05)
------------------
* Bump black from 22.10.0 to 22.12.0 by @dependabot in https://github.com/burnash/gspread/pull/1154
* Bump isort from 5.10.1 to 5.11.3 by @dependabot in https://github.com/burnash/gspread/pull/1155
* Bump isort from 5.11.3 to 5.11.4 by @dependabot in https://github.com/burnash/gspread/pull/1157
* #1104: added a delete by worksheet id method by @muddi900 in https://github.com/burnash/gspread/pull/1148
* improve CI workflow - upgrade setuptools to fix CVE by @lavigne958 in https://github.com/burnash/gspread/pull/1179
* Bump codespell from 2.2.2 to 2.2.4 by @dependabot in https://github.com/burnash/gspread/pull/1178
* Bump bandit from 1.7.4 to 1.7.5 by @dependabot in https://github.com/burnash/gspread/pull/1177
* Bump black from 22.12.0 to 23.1.0 by @dependabot in https://github.com/burnash/gspread/pull/1168
* Update user-guide.rst to include a warning by @alsaenko in https://github.com/burnash/gspread/pull/1181
* Fixed typo in docs/user-guide.rst by @raboba2re in https://github.com/burnash/gspread/pull/1182
* Bump black from 23.1.0 to 23.3.0 by @dependabot in https://github.com/burnash/gspread/pull/1183
* Handle cases when rgbColor is not set by @lavigne958 in https://github.com/burnash/gspread/pull/1184

5.7.2 (2022-12-03)
------------------
* Fix: `hidden` property might not be set from the API by @lavigne958 in https://github.com/burnash/gspread/pull/1151

5.7.1 (2022-11-17)
------------------
* Fix dependencies required version by @lavigne958 in https://github.com/burnash/gspread/pull/1147

5.7.0 (2022-11-13)
------------------
* chore: Update outdated LICENSE year by @bluzir in https://github.com/burnash/gspread/pull/1124
* add dependabot to maintain dependencies by @lavigne958 in https://github.com/burnash/gspread/pull/1126
* improve trigger on CI by @lavigne958 in https://github.com/burnash/gspread/pull/1134
* Bump bandit from 1.7.0 to 1.7.4 by @dependabot in https://github.com/burnash/gspread/pull/1133
* cancel previous run on same ref by @lavigne958 in https://github.com/burnash/gspread/pull/1135
* Bump actions/setup-python from 2 to 4 by @dependabot in https://github.com/burnash/gspread/pull/1127
* Bump actions/checkout from 2 to 3 by @dependabot in https://github.com/burnash/gspread/pull/1128
* Bump black from 22.3.0 to 22.10.0 by @dependabot in https://github.com/burnash/gspread/pull/1132
* Bump isort from 5.9.3 to 5.10.1 by @dependabot in https://github.com/burnash/gspread/pull/1131
* Bump codespell from 2.1.0 to 2.2.2 by @dependabot in https://github.com/burnash/gspread/pull/1130
* add named tuple for `DateTimeRenderOption` by @lavigne958 in https://github.com/burnash/gspread/pull/1136
* Feature/copy cut paste by @lavigne958 in https://github.com/burnash/gspread/pull/1138
* isSheetHidden method added to worksheet.py by @SazidAF in https://github.com/burnash/gspread/pull/1140

5.6.2 (2022-10-23)
------------------
* update parent folder for `client.copy` method by @lavigne958 in https://github.com/burnash/gspread/pull/1123

5.6.0 (2022-09-10)
------------------
* Fix `clear_note` method when using numeric boundaries by @lavigne958 in https://github.com/burnash/gspread/pull/1106
* Fix a typo in the permissions:create API payload by @jiananma in https://github.com/burnash/gspread/pull/1107
* Fix spreadsheet URL by @lavigne958 in https://github.com/burnash/gspread/pull/1110
* Return created permission on `Spreadsheet.share()` by @lavigne958 in https://github.com/burnash/gspread/pull/1111
* (fixed #1113) Supply correct Google API v3 permission for domains by @NickCrews in https://github.com/burnash/gspread/pull/1115
* Bugfix/numericese all by @lavigne958 in https://github.com/burnash/gspread/pull/1119

New Contributors
****************
* @jiananma made their first contribution in https://github.com/burnash/gspread/pull/1107
* @NickCrews made their first contribution in https://github.com/burnash/gspread/pull/1115

5.5.0 (2022-08-31)
------------------
* Use pathlib by @lavigne958 in https://github.com/burnash/gspread/pull/1057
* Migrate to drive API V3 by @lavigne958 in https://github.com/burnash/gspread/pull/1060
* Implement __eq__ method for `Cell` by @chisvi in https://github.com/burnash/gspread/pull/1063
* Add missing documentation on `set_timeout` by @lavigne958 in https://github.com/burnash/gspread/pull/1070
* Add method to transfer / accept ownership of a spreadsheet by @lavigne958 in https://github.com/burnash/gspread/pull/1068
* Add `client_factory` param to `auth` methods by @jlumbroso in https://github.com/burnash/gspread/pull/1075
* Fix `list_protected_ranges` by @lavigne958 in https://github.com/burnash/gspread/pull/1076
* Add function to convert column letter to column index by @lavigne958 in https://github.com/burnash/gspread/pull/1077
* Fix docstring name of named_range() param by @dgilman in https://github.com/burnash/gspread/pull/1081
* Fix grammar in docstring for client.export by @dgilman in https://github.com/burnash/gspread/pull/1080
* Many typo fixes to worksheet docstrings by @dgilman in https://github.com/burnash/gspread/pull/1083
* Fix function `numericise_all` by @lavigne958 in https://github.com/burnash/gspread/pull/1082
* Fix documentation about `oauth_from_dict` by @lavigne958 in https://github.com/burnash/gspread/pull/1088
* inherit_from_before option for insert_row/insert_rows by @yongrenjie in https://github.com/burnash/gspread/pull/1092
* add method to change the color of a tab by @lavigne958 in https://github.com/burnash/gspread/pull/1095
* docs: Fix a few typos by @timgates42 in https://github.com/burnash/gspread/pull/1094
* Fix typo in `Worksheet.batch_format` method by @lavigne958 in https://github.com/burnash/gspread/pull/1101

New Contributors
****************
* @chisvi made their first contribution in https://github.com/burnash/gspread/pull/1063
* @jlumbroso made their first contribution in https://github.com/burnash/gspread/pull/1075
* @yongrenjie made their first contribution in https://github.com/burnash/gspread/pull/1092

5.4.0 (2022-06-01)
------------------
* fix typo by @joswlv in https://github.com/burnash/gspread/pull/1031
* Fix error message in `get_all_records` by @lavigne958 in https://github.com/burnash/gspread/pull/1028
* Added feature request #1022. Auto resizing is now available for rows … by @mketer1 in https://github.com/burnash/gspread/pull/1033
* add new method to hide/show a worksheet by @lavigne958 in https://github.com/burnash/gspread/pull/1030
* feat: Download PDF from Spreadsheet #1035 by @100paperkite in https://github.com/burnash/gspread/pull/1036
* Add test on `auto_resize_columns` by @lavigne958 in https://github.com/burnash/gspread/pull/1039
* Add method to unmerge cells by @lavigne958 in https://github.com/burnash/gspread/pull/1040
* Add method to delete a protected range by @lavigne958 in https://github.com/burnash/gspread/pull/1042
* Feature/clean organize documentation by @lavigne958 in https://github.com/burnash/gspread/pull/1043
* Add warning about deprecated oauth flow by @lavigne958 in https://github.com/burnash/gspread/pull/1047
* Add new `batch_format` method. by @lavigne958 in https://github.com/burnash/gspread/pull/1049
* Encode string to utf-8 when importing CSV content by @lavigne958 in https://github.com/burnash/gspread/pull/1054

New Contributors
****************
* @joswlv made their first contribution in https://github.com/burnash/gspread/pull/1031
* @mketer1 made their first contribution in https://github.com/burnash/gspread/pull/1033
* @100paperkite made their first contribution in https://github.com/burnash/gspread/pull/1036


5.3.2 (2022-04-12)
------------------
* Bugfix/black python3.10 by @lavigne958 in https://github.com/burnash/gspread/pull/1020
* Automate releases by @lavigne958 in https://github.com/burnash/gspread/pull/1025
* Bugfix/get all record duplicated columns by @lavigne958 in https://github.com/burnash/gspread/pull/1021

5.3.0 (2022-03-28)
------------------
* Feature/rework test cassettes recording by @lavigne958 in https://github.com/burnash/gspread/pull/1004
* add method list protected ranges by @lavigne958 in https://github.com/burnash/gspread/pull/1008
* Add new methods to add/list/delete dimensionGroups by @lavigne958 in https://github.com/burnash/gspread/pull/1010
* Add method to hide rows/columns by @lavigne958 in https://github.com/burnash/gspread/pull/1012
* Add ability to rename Spreadsheets (via a new Spreadsheet.update_title) by @jansim in https://github.com/burnash/gspread/pull/1013

## New Contributors
* @jansim made their first contribution in https://github.com/burnash/gspread/pull/1013

5.2.0 (2022-02-27)
------------------
* Copy comments when during spreadsheet copy by @lavigne958 in https://github.com/burnash/gspread/pull/979
* Update user-guide.rst by @maky-hnou in https://github.com/burnash/gspread/pull/980
* merge setup test cassettes by @lavigne958 in https://github.com/burnash/gspread/pull/982
* Feature/add header validation get all records by @lavigne958 in https://github.com/burnash/gspread/pull/984
* Add timeout to client by @lavigne958 in https://github.com/burnash/gspread/pull/987
* Feature/update timezone and locale by @lavigne958 in https://github.com/burnash/gspread/pull/989
* Feature/make case comparison in find by @lavigne958 in https://github.com/burnash/gspread/pull/990
* Updated API rate limits by @hvinayan in https://github.com/burnash/gspread/pull/993
* Feature/prevent insert row to sheet with colon by @lavigne958 in https://github.com/burnash/gspread/pull/992

## New Contributors
* @maky-hnou made their first contribution in https://github.com/burnash/gspread/pull/980
* @hvinayan made their first contribution in https://github.com/burnash/gspread/pull/993

5.1.1 (2021-12-22)
------------------
* Fix documentation about oauth (#975 by @lavigne958)

5.1.0 (2021-12-22)
------------------
* Codespell skip docs build folder (#962 by @lavigne958)

* Update contributing guidelines (#964 by @lavigne958)

* Add oauth from dict (#967 by @lavigne958)

* Update README.md to include badges (#970 by @lavigne958)

* Add new method to get all values as a list of Cells (#968 by @lavigne958)

* automatic conversion of a cell letter to uppercase (#972 by @Burovytskyi)

5.0.0 (2021-11-26)
------------------
* Fix a typo in HISTORY.rst (#904 by @TurnrDev)

* Fix typo and fix return value written in docstrings (#903 by @rariyama)

* Add deprecation warning for delete_row method in documentation (#909 by @javad94)

* split files `models.py` and `test.py` (#912 by @lavigne958)

* parent 39d1ecb59ca3149a8f46094c720efab883a0dc11 author Christian Clauss <cclauss@me.com> 1621149013 +0200 commit
ter Christian Clauss <cclauss@me.com> 1630103641 +0200 (#869 by @cclaus)

* Enable code linter in CI (#915 by @lavigne958)

* isort your imports (again), so you don't have to (#914 by @cclaus)

* lint_python.yml: Try 'tox -e py' to test current Python (#916 by @cclaus)

* Add more flake8 tests (#917 by @cclaus)

* Update test suite (#918 by @cclaus)

* Avoid IndexError when row_values() returns an empty row (#920 by @cclaus)

* Bugfix - remove wrong argument in `batch_update` docstring (#912 by @lavigne958)

* Improvement - Add `Worksheet.index` property (#922 by @lavigne958)

* Add ability to create directory if it does not exist before saving the credentials to disk. (#925 by @benhoman)

* Update test framework and VCR and cassettes (#926 by @lavigne958)

* Delete .travis.yml (#928 by @cclaus)

* Update tox.ini with all linting commands under lint env (by @lavigne958)

* Build package and docs in CI (#930 by @lavigne958)

* Update oauth2.rst (#933 by @amlestin)

* Update the link to the Google Developers Console (#934 by @Croebh)

* allow tests to run on windows, add and improve tests in WorksheetTests, add test on unbounded range,
  use canonical range as specified in the API, add test cassettes, prevent InvalidGridRange,
  improve code formatting (#937 by @Fendse)

* fix fully qualified class names in API documentation (#944 by @geoffbeier)

* fix editor_users_emails - get only from list not all users added to spreadsheet (#939 by @Lukasz)

* add shadow method to get a named range from a speadsheet instance (#941 by @lavigne958)

* auto_resize_columns (#948 by @FelipeSantos75)

* add functions for defining, deleting and listing named ranges (#945 by @p-doyle)

* Implement `open` sheet within Drive folder (#951 by @datavaluepeople)

* Fix get range for unbounded ranges (#954 by @lavigne958)

* remove potential I/O when reading spreadsheet title (956 by @lavigne958)

* Add include_values_in_response to append_row & append_rows (#957 by @martimarkov)

* replace raw string "ROWS" & "COLUMNS" to Dimension named tuple,
  replace raw string "FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA" to ValueRenderOption named tuple,
  replace raw string "RAW", "USER_ENTERED" to ValueInputOption named tuple (#958 by @ccppoo)

4.0.1 (2021-08-07)
------------------

* Do not overwrite original value when trying to convert to a number (#902 by @lavigne958)


4.0.0 (2021-08-01)
------------------

* Changed `Worksheet.find()` method returns `None` if nothing is found (#899 by @GastonBC)

* Add `Worksheet.batch_clear()` to clear multiple ranges. (#897 by @lavigne958)

* Fix `copy_permission` argument comparison in `Client.copy()` method (#898 by @lavigne958)

* Allow creation of spreadhsheets in a shared drive (#895 by @lavigne958)

* Allow `gspread.oauth()` to accept a custom credential file (#891 by @slmtpz)

* Update `tox.ini`, remove python2 from env list (#887 by @cclaus)

* Add `SpreadSheet.get_worksheet_by_id()` method (#857 by @a-crovetto)

* Fix `store_credentials()` when `authorized_user_filename` is passed (#884 by @neuenmuller)

* Remove python2 (#879 by @lavigne958)

* Use `Makefile` to run tests (#883 by @lavigne958)

* Update documentation `Authentication:For End Users` using OAuth Client ID (#835 by @ManuNaEira)

* Allow fetching named ranges from `Worksheet.range()` (#809 by @agatti)

* Update README to only mention python3.3+ (#877 by @lavigne958)

* Fetch `creation` and `lastUpdate` time from `SpreadSheet` on open (#872 by @lavigne958)

* Fix bug with `Worksheet.insert_row()` with `value_input_option` argument (#873 by @elijabesu)

* Fix typos in doc and comments (#868 by @cclauss)

* Auto cast numeric values from sheet cells to python int or float (#866 by @lavigne958)

* Add `Worksheet.get_values()` method (#775 by @burnash)

* Allow `gspread.oauth()` to accept a custom filename (#847 by @bastienboutonnet)

* Document dictionary credentials auth (#860 by @dmytrostriletskyi)

* Add `Worksheet.get_note()` (#855 by @water-ghosts )

* Add steps for creating new keys (#856 by @hanzala-sohrab)

* Add `folder_id` argument to `Client.copy()` (#851 by @punnerud)

* Fix typos in docstrings (#848 by @dgilman)

3.7.0 (2021-02-18)
------------------

* Add `Worksheet.insert_note()`, `Worksheet.update_note()`, `Worksheet.clear_note()` (#818 by @lavigne958)

* Update documentation: oauth2.rst (#836 by @Prometheus3375)

* Documentation fixes (#838 by @jayeshmanani)

* Documentation fixes (#845 by @creednaylor)

* Add `Worksheet.insert_cols()` (#802 by @AlexeyDmitriev)

* Documentation fixes (#814 by @hkuffel)

* Update README.md (#811 by @tasawar-hussain)

* Add `value_render_option` parameter to `Worksheet.get_all_records()` (#776 by @damgad)

* Remove `requests` from `install_requires` (#801)

* Simplify implementation of `Worksheet.insert_rows()` (#799 by @AlexeyDmitriev)

* Add `auth.service_account_from_dict()` (#785 b7 @mahenzon)

* Fix `ValueRange.from_json()` (#791 by @erakli)

* Update documentation: oauth2.rst (#794 by @elnjensen)

* Update documentation: oauth2.rst (#789 by @Takur0)

* Allow `auth` to be `None`. Fix #773 (#774 by @lepture)


3.6.0 (2020-04-30)
------------------

* Add `Worksheet.insert_rows()` (#734 by @tr-fi)

* Add `Worksheet.copy_to()` (#758 by @JoachimKoenigslieb)

* Add ability to create a cell instance using A1 notation (#765 by @tivaliy)

* Add `auth.service_account()` (#768)

* Add Authlib usage (#552 by @lepture)


3.5.0 (2020-04-23)
------------------

* Simplified OAuth2 flow (#762)

* Fix `Worksheet.delete_rows()` index error (#760 by @rafa-guillermo)

* Deprecate `Worksheet.delete_row()` (#766)

* Scope `Worksheet.find()` to a specific row or a column (#739 by @alfonsocv12)

* Add `Worksheet.add_protected_range()` #447 (#720 by @KesterChan01)

* Add ability to fetch cell address in A1 notation (#763 by @tivaliy)

* Add `Worksheet.delete_columns()` (#761 by @rafa-guillermo)

* Ignore numericising specific columns in `get_all_records` (#701 by @benjamindhimes)

* Add option ``folder_id`` when creating a spreadsheet (#754 by @Abdellam1994)

* Add `insertDataOption` to `Worksheet.append_row()` and `Worksheet.append_rows()` (#719 by @lobatt)


3.4.2 (2020-04-06)
------------------

* Fix Python 2 `SyntaxError` in models.py #751 (#752)


3.4.1 (2020-04-05)
------------------

* Fix `TypeError` when using gspread in google colab (#750)


3.4.0 (2020-04-05)
------------------

* Remove `oauth2client` in favor of `google-auth` #472, #529 (#637 by @BigHeadGeorge)
* Convert `oauth2client` credentials to `google-auth` (#711 by @aiguofer)
* Remove unnecessary `login()` from `gspread.authorize`

* Fix sheet name quoting issue (#554, #636, #716):
    * Add quotes to worksheet title for get_all_values (#640 by @grlbrwrg, #717 by @zynaxsoft)
    * Escaping title containing single quotes with double quotes (#730 by @vijay-shanker)
    * Use `utils.absolute_range_name()` to handle range names (#748)

* Fix `numericise()`: add underscores test to work in python2 and <python3.6 (#622 by @epicfaace)

* Add `supportsAllDrives` to Drive API requests (#709 by @justinr1234)

* Add `Worksheet.merge_cells()` (#713 by @lavigne958)
* Improve `Worksheet.merge_cells()` and add `merge_type` parameter (#742 by @aiguofer)

* Add `Worksheet.sort()` (#639 by @kirillgashkov)

* Add ability to reorder worksheets #570 (#571 by @robin900)
    * Add `Spreadsheet.reorder_worksheets()`
    * Add `Worksheet.update_index()`

* Add `test_update_cell_objects` (#698 by @ogroleg)

* Add `Worksheet.append_rows()` (#556 by @martinwarby, #694 by @fabytm)

* Add `Worksheet.delete_rows()` (#615 by @deverlex)

* Add Python 3.8 to Travis CI (#738 by @artemrys)

* Speed up `Client.open()` by querying files by title in Google Drive (#684 by @aiguofer)

* Add `freeze`, `set_basic_filter` and `clear_basic_filter` methods to `Worksheet` (#574 by @aiguofer)

* Use Drive API v3 for creating and deleting spreadsheets (#573 by @aiguofer)

* Implement `value_render_option` in `get_all_values` (#648 by @mklaber)

* Set position of a newly added worksheet (#688 by @djmgit)
* Add url properties for `Spreadsheet` and `Worksheet` (#725 by @CrossNox)

* Update docs: "APIs & auth" menu deprecation, remove outdated images in oauth2.rst (#706 by @manasouza)


3.3.1 (2020-04-01)
------------------

* Support old and new collections.abc.Sequence in `utils` (#745 by @timgates42)


3.3.0 (2020-03-12)
------------------

* Added `Spreadsheet.values_batch_update()` (#731)
* Added:
    * `Worksheet.get()`
    * `Worksheet.batch_get()`
    * `Worksheet.update()`
    * `Worksheet.batch_update()`
    * `Worksheet.format()`

* Added more parameters to `Worksheet.append_row()` (#719 by @lobatt, #726)
* Fix usage of client.openall when a title is passed in (#572 by @aiguofer)


3.2.0 (2020-01-30)
------------------

* Fixed `gspread.utils.cell_list_to_rect()` on non-rect cell list (#613 by @skaparis)
* Fixed sharing from Team Drives (#646 by @wooddar)
* Fixed KeyError in list comprehension in `Spreadsheet.remove_permissions()` (#643 by @wooddar)
* Fixed typos in docstrings and a docstring type param (#690 by @pedrovhb)
* Clarified supported Python versions (#651 by @hugovk)
* Fixed the Exception message in `APIError` class (#634 by @lordofinsomnia)
* Fixed IndexError in `Worksheet.get_all_records()` (#633 by @AivanF)

* Added `Spreadsheet.values_batch_get()` (#705 by @aiguofer)


3.1.0 (2018-11-27)
------------------

* Dropped Python 2.6 support

* Fixed `KeyError` in `urllib.quote` in Python 2 (#605, #558)
* Fixed `Worksheet.title` being out of sync after using `update_title` (#542 by @ryanpineo)
* Fix parameter typos in docs (#616 by @bryanallen22)
* Miscellaneous docs fixes (#604 by @dgilman)
* Fixed typo in docs (#591 by @davidefiocco)

* Added a method to copy spreadsheets (#625 by @dsask)
* Added `with_link` attribute when sharing / adding permissions (#621 by @epicfaace)
* Added ability to duplicate a worksheet (#617)
* Change default behaviour of numericise function #499 (#502 by @danthelion)
* Added `stacklevel=2` to deprecation warnings


3.0.1 (2018-06-30)
------------------

* Fixed #538 (#553 by @ADraginda)


3.0.0 (2018-04-12)
------------------

* This version drops Google Sheets API v3 support.
    - API v4 was the default backend since version 2.0.0.
    - All v4-related code has been moved from `gspread.v4` module to `gspread` module.


2.1.1 (2018-04-08)
------------------

* Fixed #533 (#534 by @reallistic)


2.1.0 (2018-04-07)
------------------

* URL encode the range in the value_* functions (#530 by @aiguofer)
* Open team drive sheets by name (#527 by @ryantuck)


2.0.1 (2018-04-01)
------------------

* Fixed #518
* Include v4 in setup.py
* Fetch all spreadsheets in Spreadsheet.list_spreadsheet_files (#522 by @aiguofer)


2.0.0 (2018-03-11)
------------------

* Ported the library to Google Sheets API v4.

  This is a transition release. The v3-related code is untouched,
  but v4 is used by default. It is encouraged to move to v4 since
  the API is faster and has more features.

  API v4 is a significant change from v3. Some methods are not
  backward compatible, so there's no support for this compatibility
  in gspread either.

  These methods and properties are not supported in v4:

  * `Spreadsheet.updated`
  * `Worksheet.updated`
  * `Worksheet.export()`
  * `Cell.input_value`


0.6.2 (2016-12-20)
------------------

* Remove deprecated HTTPError

0.6.1 (2016-12-20)
------------------

* Fixed error when inserting permissions #431

0.6.0 (2016-12-15)
------------------

* Added spreadsheet sharing functionality
* Added csv import
* Fixed bug where list of sheets isn't cleared on refetch
  #429, #386


0.5.1 (2016-12-12)
------------------

* Fixed a missing return value in `utils.a1_to_rowcol`
* Fixed url parsing in `Client.open_by_url`
* Added `updated` property to `Spreadsheet` objects


0.5.0 (2016-12-12)
------------------

* Added method to create blank spreadsheets #253
* Added method to clear worksheets #156
* Added method to delete a row in a worksheet #337
* Changed `Worksheet.range` method to accept integers as coordinates #142
* Added `default_blank` parameter to `Worksheet.get_all_records` #423
* Use xml.etree.cElementTree when available to reduce memory usage #348
* Fixed losing input_value data from following cells in `Worksheet.insert_row` #338
* Deprecated `Worksheet.get_int_addr` and `Worksheet.get_addr_int`
  in favour of `utils.a1_to_rowcol` and `utils.rowcol_to_a1` respectively


0.4.1 (2016-07-17)
------------------

* Fix exception format to support Python 2.6


0.4.0 (2016-06-30)
------------------

* Use request session's connection pool in HTTPSession

* Removed deprecated ClientLogin


0.3.0 (2015-12-15)
------------------

* Use Python requests instead of the native HTTPConnection object

* Optimized row_values and col_values

* Optimized row_values and col_values
  Removed the _fetch_cells call for each method. This eliminates the
  adverse effect on runtime for large worksheets.

  Fixes #285, #190, #179, and #113

* Optimized row_values and col_values
  Removed the _fetch_cells call for each method. This eliminates the
  adverse effect on runtime for large worksheets.

  Fixes #285, #190, #179, and #113

* Altered insert_row semantics to utilize range
  This avoids issuing one API request per cell to retrieve the Cell
  objects after the insertion row. This provides a significant speed-up
  for insertions at the beginning of large sheets.

* Added mock tests for Travis (MockSpreadsheetTest)

* Fixed XML header issue with Python 3

* Fixed Worksheet.export function and associated test

* Added spreadsheet feed helper

* Add CellNotFound to module exports
  Fixes #88

* Fixed utf8 encoding error caused by duplicate XML declarations
* Fixed AttributeError when URLError caught by HTTPError catch block
  Fixes #257

* Added __iter__ method to Spreadsheet class

* Fixed export test
* Switched tests to oauth

0.2.5 (2015-04-22)
------------------

* Deprecation warning for ClientLogin #210
* Redirect github pages to ReadTheDocs
* Bugfixes

0.2.4 (2015-04-17)
------------------

* Output error response #219 #170 #194.
* Added instructions on how to get oAuth credentials to docs.

0.2.3 (2015-03-11)
------------------

* Fixed issue with `Spreadsheet.del_worksheet`.
* Automatically refresh OAuth2 token when it has expired.
* Added an `insert_row` method to `Worksheet`.
* Moved docs to Read The Docs.
* Added the `numeric_value` attribute to `Cell`.
* Added title property to `Spreadsheet`.
* Support for exporting worksheets.
* Added row selection for keys in `Worksheet.get_all_records`.

0.2.2 (2014-08-26)
------------------

* Fixed version not available for read-only spreadsheets bug

0.2.1 (2014-05-10)
------------------

* Added OAuth2 support
* Fixed regression bug #130. Not every POST needs If-Match header

0.2.0 (2014-05-09)
------------------

* New Google Sheets support.
* Fixed get_all_values() on empty worksheet.
* Bugfix in get_int_addr().
* Changed the HTTP connectivity from urllib to httlib for persistent http connections.

0.1.0 (2013-07-09)
------------------

* Support for deleting worksheets from a spreadsheet.

0.0.15 (2013-02-01)
------------------

* Couple of bugfixes.

0.0.14 (2013-01-31)
------------------

* Bugfix in Python 3.


0.0.12 (2011-12-25)
------------------

* Python 3 support.


0.0.9 (2011-12-16)
------------------

* Enter the Docs.
* New skinnier login method.


0.0.7 (2011-12-14)
------------------

* Pypi install bugfix.


0.0.6 (2011-12-13)
------------------

* Batch cells update.


0.0.2 (2011-12-12)
------------------

* New spreadsheet open methods:

    - Client.open_by_key
    - Client.open_by_url


0.0.1 (2011-12-12)
------------------

* Got rid of the wrapper.
* Support for pluggable http session object.


pre 0.0.1 (2011-12-02)
----------------------

* Hacked a wrapper around Google's Python client library.
