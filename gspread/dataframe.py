from .ns import _ns, _ns1, ATOM_NS, BATCH_NS, SPREADSHEET_NS
from .utils import finditem, numericise as num

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
import itertools
import logging

logger = logging.getLogger(__name__)

# If pandas is absent, this module will load without raising an error.
# Only if the set_with_dataframe or get_as_dataframe functions are called will
# an ImportError be raised mentioning the missing module.
try:
    import pandas as pd
    import re
    major, minor = map(
        int,
        re.search(r'^(\d+)\.(\d+)\..+$', pd.__version__).groups()
        )
    if (major, minor) < (0, 14):
        raise ImportError("pandas version too old to support DF operations")
    logger.debug(
        "Imported satisfactory (>=0.14.0) Pandas module: %s",
        pd.__version__)
except ImportError:
    class _MissingPandasModule():
        def __getattr__(self, name):
            raise ImportError("Missing module named 'pandas'; using "
            "gspread.dataframe functions requires pandas >= 0.14.0")
    pd = _MissingPandasModule()

__all__ = ('set_with_dataframe', 'get_as_dataframe')

CELLS_FEED_REL = SPREADSHEET_NS + '#cellsfeed'
GOOGLE_SHEET_CELL_UPDATES_LIMIT = 40000

def _cellrepr(value, allow_formulas):
    """
    Get a string representation of dataframe value.

    :param :value: the value to represent
    :param :allow_formulas: if True, allow values starting with '='
            to be interpreted as formulas; otherwise, escape
            them with an apostrophe to avoid formula interpretation.
    """
    if pd.isnull(value):
        return ""
    value = str(value)
    if (not allow_formulas) and value.startswith('='):
        value = "'{value}".format(value=value)
    return value

def _resize_to_minimum(worksheet, rows=None, cols=None):
    """
    Resize the worksheet to guarantee a minimum size, either in rows,
    or columns, or both.

    Both rows and cols are optional.
    """
    # get the current size
    feed = worksheet.client.get_cells_feed(worksheet)

    current_cols, current_rows = (
        num(feed.find(_ns1('colCount')).text),
        num(feed.find(_ns1('rowCount')).text),
        )
    if rows is not None and rows <= current_rows:
        rows = None
    if cols is not None or cols <= current_cols:
        cols = None

    if cols is not None or rows is not None:
        worksheet.resize(rows, cols)

def get_as_dataframe(worksheet,
                     index_column_number=None,
                     has_column_header=True,
                     evaluate_formulas=False,
                     numericise=True):
    """
    Returns the worksheet contents as a DataFrame.

    :param worksheet: the worksheet.
    :param index_column_number: if >0, the worksheet column number to use
            as the DataFrame index. (First column in worksheet is column 1.)
            If absent or false, the DataFrame index will be
            Defaults to None.
    :param has_column_header: if True, interpret the first row of
            the worksheet as containing the names of columns for the
            DataFrame. Defaults to True.
    :param evaluate_formulas: if True, get the value of a cell after
            formula evaluation; otherwise get the formula itself if present.
            Defaults to False.
    :param numericise: if True, when cells can be interpreted as numeric
            values, use true numeric objects in the DataFrame. Defaults
            to True.
    :returns: pandas.DataFame
    """
    cell_feed = worksheet.client.get_cells_feed(worksheet)

    df = pd.DataFrame()
    value_func = num if numericise else lambda x: x
    for cell in cell_feed.findall(_ns('entry')):
        gs = cell.find(_ns1('cell'))
        if evaluate_formulas:
            cell_value = value_func(list(gs.itertext())[0])
        else:
            cell_value = value_func(gs.get('inputValue'))
        column = num(gs.get('col'))
        row = num(gs.get('row'))

        df.loc[row, column] = cell_value

    if not df.empty:
        df = df.reindex(columns=list(range(1, max(df.columns)+1)))

        if has_column_header:
            df.columns = df.iloc[0]
            df.columns.name = None
            df = df.drop(1)

        df.index = list(range(1, len(df)+1))

        if index_column_number and len(df):
            if index_column_number < 1 or \
               index_column_number > len(df.columns):
                raise ValueError("index_column must reference number of "
                    "an existing column, not %s" % index_column_number)
            df.index = df[df.columns[index_column_number-1]]
            del df[df.columns[index_column_number-1]]

    return df

def set_with_dataframe(worksheet,
                       dataframe,
                       row=1,
                       col=1,
                       include_index=True,
                       include_column_header=True,
                       resize=False,
                       allow_formulas=True):
    """
    Sets the values of a given DataFrame, anchoring its upper-left corner
    at (row, col). (Default is row 1, column 1.)

    :param worksheet: the gspread worksheet to set with content of DataFrame.
    :param dataframe: the DataFrame.
    :param include_index: if True, include the DataFrame's index as an
            additional column. Defaults to True.
    :param include_column_header: if True, add a header row before data with
            column names. If include_index is True, the index's name will be
            used as its column's header. Defaults to True.
    :param resize: if True, changes the worksheet's size to match the shape
            of the provided DataFrame. If False, worksheet will only be
            resized as necessary to contain the DataFrame contents.
            Defaults to False.
    :param allow_formulas: if True, interprets `=foo` as a formula in
            cell values; otherwise all text beginning with `=` is escaped
            to avoid its interpretation as a formula. Defaults to True.
    """
    # x_pos, y_pos refers to the position of data rows only,
    # excluding any header rows in the google sheet.
    # If header-related params are True, the values are adjusted
    # to allow space for the headers.
    y, x = dataframe.shape
    if include_index:
        col += 1
    if include_column_header:
        row += 1
    if resize:
        worksheet.resize(y + row - 1, x + col - 1)
    else:
        _resize_to_minimum(worksheet, y + row - 1, x + col - 1)

    updates = []

    if include_column_header:
        for idx, val in enumerate(dataframe.columns):
            updates.append(
                (row - 1,
                 col+idx,
                 _cellrepr(val, allow_formulas))
            )
    if include_index:
        for idx, val in enumerate(dataframe.index):
            updates.append(
                (idx+row,
                 col-1,
                 _cellrepr(val, allow_formulas))
            )
        if include_column_header:
            updates.append(
                (row-1,
                 col-1,
                 _cellrepr(dataframe.index.name, allow_formulas))
            )

    for y_idx, value_row in enumerate(dataframe.values):
        for x_idx, cell_value in enumerate(value_row):
            updates.append(
                (y_idx+row,
                 x_idx+col,
                 _cellrepr(cell_value, allow_formulas))
            )

    if not updates:
        logger.debug("No updates to perform on worksheet.")
        return

    # Google limits cell update requests such that the submitted
    # set of updates cannot contain 40,000 cells or more.
    # Make update batches with less than 40,000 elements.
    update_batches = [
        updates[x:x+GOOGLE_SHEET_CELL_UPDATES_LIMIT]
        for x in range(0, len(updates), GOOGLE_SHEET_CELL_UPDATES_LIMIT)
        ]
    logger.debug("%d cell updates to send, will send %d batches of "
        "%d cells maximum", len(updates), len(update_batches), GOOGLE_SHEET_CELL_UPDATES_LIMIT)

    for batch_num, update_batch in enumerate(update_batches):
        batch_num += 1
        logger.debug("Sending batch %d of cell updates", batch_num)
        feed = Element('feed', {
            'xmlns': ATOM_NS,
            'xmlns:batch': BATCH_NS,
            'xmlns:gs': SPREADSHEET_NS
            })

        id_elem = SubElement(feed, 'id')
        id_elem.text = (
            finditem(
                lambda i: i.get('rel') == CELLS_FEED_REL,
                worksheet._element.findall(_ns('link'))
            ).get('href')
            )
        for rownum, colnum, input_value in update_batch:
            code = 'R{}C{}'.format(rownum, colnum)
            entry = SubElement(feed, 'entry')
            SubElement(entry, 'batch:id').text = code
            SubElement(entry, 'batch:operation', {'type': 'update'})
            SubElement(entry, 'id').text = id_elem.text + '/' + code
            SubElement(entry, 'link', {
                'rel': 'edit',
                'type': "application/atom+xml",
                'href': id_elem.text + '/' + code})

            SubElement(entry, 'gs:cell', {
                'row': str(rownum),
                'col': str(colnum),
                'inputValue': input_value})

        data = ElementTree.tostring(feed)

        worksheet.client.post_cells(worksheet, data)

    logger.debug("%d total update batches sent", len(update_batches))

