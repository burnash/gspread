"""
gspread.models
~~~~~~~~~~~~~~

This module contains common cells' models.

"""

from .utils import a1_to_rowcol, numericise, rowcol_to_a1


class Cell:
    """An instance of this class represents a single cell
    in a :class:`worksheet <gspread.models.Worksheet>`.
    """

    def __init__(self, row, col, value=""):
        self._row = row
        self._col = col

        #: Value of the cell.
        self.value = value

    @classmethod
    def from_address(cls, label, value=""):
        return cls(*a1_to_rowcol(label), value=value)

    def __repr__(self):
        return "<{} R{}C{} {}>".format(
            self.__class__.__name__,
            self.row,
            self.col,
            repr(self.value),
        )

    @property
    def row(self):
        """Row number of the cell."""
        return self._row

    @property
    def col(self):
        """Column number of the cell."""
        return self._col

    @property
    def numeric_value(self):
        numeric_value = numericise(self.value, default_blank=None)

        # if could not convert, return None
        if type(numeric_value) == int or type(numeric_value) == float:
            return numeric_value
        else:
            return None

    @property
    def address(self):
        """Cell address in A1 notation."""
        return rowcol_to_a1(self.row, self.col)

    @property
    def input_value(self):
        """.. deprecated:: 2.0

        This feature is not supported in Sheets API v4.
        """
        import warnings

        warnings.warn(
            "Cell.input_value is deprecated, "
            "this feature is not supported in Sheets API v4. "
            "Please use `value_render_option` when you "
            "Retrieve `Cell` objects (e.g. in `Worksheet.range()` method).",
            DeprecationWarning,
            stacklevel=2,
        )
