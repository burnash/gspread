"""
gspread.cell
~~~~~~~~~~~~

This module contains common cells' models.

"""

from typing import Optional, Union

from .utils import a1_to_rowcol, numericise, rowcol_to_a1


class Cell:
    """An instance of this class represents a single cell
    in a :class:`~gspread.worksheet.Worksheet`.
    """

    def __init__(self, row: int, col: int, value: Optional[str] = "") -> None:
        self._row: int = row
        self._col: int = col

        #: Value of the cell.
        self.value: Optional[str] = value

    @classmethod
    def from_address(cls, label: str, value: str = "") -> "Cell":
        """Instantiate a new :class:`~gspread.cell.Cell`
        from an A1 notation address and a value

        :param string label: the A1 label of the returned cell
        :param string value: the value for the returned cell
        :rtype: Cell
        """
        row, col = a1_to_rowcol(label)
        return cls(row, col, value)

    def __repr__(self) -> str:
        return "<{} R{}C{} {}>".format(
            self.__class__.__name__,
            self.row,
            self.col,
            repr(self.value),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cell):
            return False

        same_row = self.row == other.row
        same_col = self.col == other.col
        same_value = self.value == other.value
        return same_row and same_col and same_value

    @property
    def row(self) -> int:
        """Row number of the cell.

        :type: int
        """
        return self._row

    @property
    def col(self) -> int:
        """Column number of the cell.

        :type: int
        """
        return self._col

    @property
    def numeric_value(self) -> Optional[Union[int, float]]:
        """Numeric value of this cell.

        Will try to numericise this cell value,
        upon success will return its numeric value
        with the appropriate type.

        :type: int or float
        """
        numeric_value = numericise(self.value, default_blank=None)

        # if could not convert, return None
        if isinstance(numeric_value, int) or isinstance(numeric_value, float):
            return numeric_value
        else:
            return None

    @property
    def address(self) -> str:
        """Cell address in A1 notation.

        :type: str
        """
        return rowcol_to_a1(self.row, self.col)
