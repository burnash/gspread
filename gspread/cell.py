"""
gspread.cell
~~~~~~~~~~~~

This module contains common cells' models.

"""

from .utils import a1_to_rowcol, numericise, rowcol_to_a1


class Cell:
    """An instance of this class represents a single cell
    in a :class:`~gspread.worksheet.Worksheet`.
    """

    def __init__(self, row, col, value=""):
        self._row = row
        self._col = col

        #: Value of the cell.
        self.value = value

    @classmethod
    def from_address(cls, label, value=""):
        """Instantiate a new :class:`~gspread.cell.Cell`
        from an A1 notation address and a value

        :param string label: the A1 label of the returned cell
        :param string value: the value for the returned cell
        :rtype: Cell
        """
        return cls(*a1_to_rowcol(label), value=value)

    def __repr__(self):
        return "<{} R{}C{} {}>".format(
            self.__class__.__name__,
            self.row,
            self.col,
            repr(self.value),
        )

    def __eq__(self, other):
        same_row = self.row == other.row
        same_col = self.col == other.col
        same_value = self.value == other.value
        return same_row and same_col and same_value

    @property
    def row(self):
        """Row number of the cell.

        :type: int
        """
        return self._row

    @property
    def col(self):
        """Column number of the cell.

        :type: int
        """
        return self._col

    @property
    def numeric_value(self):
        """Numeric value of this cell.

        Will try to numericise this cell value,
        upon success will return its numeric value
        with the appropriate type.

        :type: int or float
        """
        numeric_value = numericise(self.value, default_blank=None)

        # if could not convert, return None
        if type(numeric_value) == int or type(numeric_value) == float:
            return numeric_value
        else:
            return None

    @property
    def address(self):
        """Cell address in A1 notation.

        :type: str
        """
        return rowcol_to_a1(self.row, self.col)
