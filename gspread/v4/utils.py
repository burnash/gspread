from collections import defaultdict
from itertools import chain


def rightpad(row, max_len):
    pad_len = max_len - len(row)
    return row + ([''] * pad_len) if pad_len != 0 else row


def fill_gaps(L, rows=None, cols=None):

    max_cols = max(len(row) for row in L) if cols is None else cols
    max_rows = len(L) if rows is None else rows

    pad_rows = max_rows - len(L)

    if pad_rows:
        L = L + ([[]] * pad_rows)

    return [rightpad(row, max_cols) for row in L]


def cell_list_to_rect(cell_list):
    if not cell_list:
        return []

    rows = defaultdict(lambda: defaultdict(str))

    row_offset = cell_list[0].row
    col_offset = cell_list[0].col

    for cell in cell_list:
        row = rows.setdefault(int(cell.row) - row_offset, defaultdict(str))
        row[cell.col - col_offset] = cell.value

    if not rows:
        return []

    all_row_keys = chain.from_iterable(row.keys() for row in rows.values())
    rect_cols = range(max(all_row_keys) + 1)
    rect_rows = range(max(rows.keys()) + 1)

    return [[rows[i][j] for j in rect_cols] for i in rect_rows]
