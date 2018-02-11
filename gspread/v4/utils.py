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
