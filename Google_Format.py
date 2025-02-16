import gspread
from oauth2client.service_account import ServiceAccountCredentials


class Sheet:
    # The api is the credentials you downloaded from Google
    # and The key is the Google url key used to get access to the spreadsheet
    def __init__(self, api, key):
        # Define the scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        # Getting information from the api file
        credentials = ServiceAccountCredentials.from_json_keyfile_name(api, scope)

        # Authorize the client for Accesses into the Sheet
        client = gspread.authorize(credentials)

        # Having the correct Google sheet url to edit in
        spreadsheet = client.open_by_url(key)

        # This is the official Spread Sheet
        self.sheet = spreadsheet

        # First Sheet being edit inside the SpreadSheet
        self.worksheet = spreadsheet.sheet1

    # Getting the color by string or tuple
    @staticmethod
    def get_color(rbg: str or tuple) -> tuple:
        if rbg is str:
            rbg.lower()
        # Green
        if rbg == "green":
            rbg = (0, 255, 0)
        # Red
        elif rbg == "red":
            rbg = (255, 0, 0)
        # Yellow
        elif rbg == "yellow":
            rbg = (255, 255, 0)
        # Orange
        elif rbg == "orange":
            rbg = (255, 153, 0)
        # Pink
        elif rbg == "pink":
            rbg = (255, 0, 255)
        # Blue
        elif rbg == "blue":
            rbg = (0, 0, 255)

        # Ligth Blue
        elif rbg == "light blue":
            rbg = (173, 216, 230)
        # Black
        elif rbg == "black":
            rbg = (0, 0, 0)
        # White
        elif rbg == "white" or rbg == "":
            rbg = (255, 255, 255)
        # No color selected
        else:
            rbg = (0, 0, 0)

        # just because I like the simple (255,255,255) you are expose to use (1, 0.2, 0)
        rbg = (rbg[0] / 255, rbg[1] / 255, rbg[2] / 255)
        return rbg

    # Cell Number
    @staticmethod
    def locate(cell: str) -> tuple:
        # Cells row
        cell_row = cell[0].upper()

        # Cells column
        cell_col = cell[1:]

        # Abc to find the location number of Cell row
        abc = "".join([chr(64 + i) for i in range(1, 27)])
        return abc, abc.find(cell_row), int(cell_col)

    # Cell Background
    def fill(self, cell, color) -> None:
        # Getting the color
        # Checking to see if this is a list and if it is
        # You can fill in multiple colors as once
        if isinstance(color, list):
            formats_lst = []
            abc, cell_x, cell_y = self.locate(cell)
            y = 0
            for col in color:
                x = 0
                for color in col:
                    cell = f"{abc[cell_x + x]}{cell_y + y}"

                    # Getting the color
                    color = self.get_color(color)

                    # Setting up method to be used in batch_format
                    update = {
                        "range": cell,
                        "format": {
                            "backgroundColor": {
                                "red": color[0],
                                "green": color[1],
                                "blue": color[2]
                            }
                        }
                    }

                    formats_lst.append(update)
                    x += 1
                y += 1
            # Once for loop finishes getting all the colors it will update it all the cells at once
            self.worksheet.batch_format(formats_lst)

        # if this is not a list it will run as a str, tuple and so on
        else:
            # Getting the color
            color = self.get_color(color)

            # Filling in the cell background
            self.worksheet.format(cell, {
                "backgroundColor": {
                    "red": color[0],
                    "green": color[1],
                    "blue": color[2]
                }})

    # Cell Writing and TextColor changing and Bold
    def write(self, cell, text="", bold=False, color=False) -> None:

        # Writing text for the cell
        self.worksheet.update_acell(cell, text)

        # Getting color
        color = self.get_color(color)

        self.worksheet.format(cell, {
            "textFormat": {
                "bold": bold,
                "foregroundColor": {
                    "red": color[0],
                    "green": color[1],
                    "blue": color[2]
                }
            }
        })

    # Cell Uploading List
    def load(self, cell, lst, lst_spc: int = False, bold=False, color=False, center=False) -> None:
        # Good for loading list of values
        self.worksheet.update(cell, lst)

        # Getting color
        color = self.get_color(color)

        # Getting specific cell location
        abc, cell_x, cell_y = self.locate(cell)

        # Getting the complete list cell beginning and ending
        if lst_spc:
            lst_spc -= 1
            cell = f"{abc[cell_x]}{cell_y + lst_spc}:{abc[cell_x + len(lst[lst_spc]) - 1]}{cell_y + lst_spc}"
        else:
            # Getting full list length
            cell = f"{cell}:{abc[cell_x + len(max(lst, key=len))]}{cell_y + len(lst)}"

        # Changing color and boldness
        self.worksheet.format(cell, {
            "textFormat": {
                "bold": bold,
                "foregroundColor": {
                    "red": color[0],
                    "green": color[1],
                    "blue": color[2]
                }
            }
        })

        if center:
            if isinstance(center, bool):
                center = "center"
            self.center(cell, center)

    # Sum
    def sum(self, cell, value: str or tuple) -> None:
        # if there is a bunch of cells you want to add together this will add them
        if isinstance(value, tuple):
            value = ",".join(value)

        self.write(cell, f"=sum({value})")

    # Finding cell location
    def find(self, text: str) -> str:
        # Getting the value of all the cells
        all_cells = self.worksheet.get_all_values()

        # Using the enumerate function to keep up with the index and row
        for row_index, row in enumerate(all_cells, start=1):
            # Using it again to get the Index of the col to get the right Letter
            for col_index, col in enumerate(row, start=1):

                # Checking to see if This is the correct value
                if col == text:
                    # returning the row and col with chr
                    # chr is just a built-in module with letters and numbers
                    # you don't hit the alphabet until 64 characters in
                    return f"{chr(64 + col_index)}{row_index}"

    # Getting Value
    def get(self, cell: str) -> None:
        # Returning value of the cell
        return self.worksheet.get(cell)

    # Clear
    def clear(self, cell: str = False) -> None:
        # Checks to see if you want a specific cell erased or all of it
        if cell:
            self.worksheet.batch_clear([cell])
        else:
            # whole sheet
            cell = "1:1000"
            self.worksheet.clear()

        # Erasing the Text color and Bolding
        # Erasing the Background color
        # Resetting horizontalAlignment, Boarders & NumberFormat
        self.worksheet.format(cell, {
            "textFormat": {
                "bold": False,
                "foregroundColor": {
                    "red": 0,
                    "green": 0,
                    "blue": 0
                }
            },
            "backgroundColor": {
                "red": 1,
                "green": 1,
                "blue": 1
            },
            "horizontalAlignment": None,
            "borders": None,
            "numberFormat": None
        })

        # Unmerging All Cells
        self.worksheet.unmerge_cells(cell)

    # Centering
    def center(self, cell, side: str = False) -> None:
        # Checking to see if args is being used
        if not side:
            side = "center"

        # Uppercase everything
        side = side.upper()

        # Changing the cell horizontal alignment
        self.worksheet.format(cell, {
            "horizontalAlignment": side
        })

    # Merging
    def merge(self, cell):
        # Merging cells
        self.worksheet.merge_cells(cell)

    # Bolding
    def bold(self, cell, bold=True):
        self.worksheet.format(cell, {
            "textFormat": {
                "bold": bold
            }
        })

    # Boarders
    def borders(self, cell):
        # Borders are all Solid
        self.worksheet.format(cell, {
            "borders": {
                "top": {"style": "SOLID"},
                "bottom": {"style": "SOLID"},
                "left": {"style": "SOLID"},
                "right": {"style": "SOLID"},
            }
        })

    # Format for Money or other
    def format(self, cell: str = False, format: str = "None") -> None:
        if not cell:
            cell = "1:1000"

        else:
            format = format.upper()

        self.worksheet.format(cell, {
            "numberFormat": {
                "type": format
            }
        })

    # New SpreadSheet
    def new_sheet(self, name: str) -> None:
        try:
            self.worksheet = self.sheet.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            print(f"worksheet {name} not found")

    # Add SpreadSheet
    def add_sheet(self, name: str) -> None:
        try:
            self.sheet.add_worksheet(name, 1000, 27)
        except gspread.exceptions.APIError:
            print("Sheet already exists")

    # Delete SpreadSheet
    def del_sheet(self, name: str) -> None:
        try:
            name = self.sheet.worksheet(name)
            self.sheet.del_worksheet(name)
        except gspread.exceptions.APIError:
            print("Sheet does not exist")
