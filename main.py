"""
Sudoku Solver
reads in a 9x9 sudoku square with blanks filled in as '0'
separates the puzzle into 9 rows, 9 columns, and 9 3x3 squares
rows, columns, and squares will be made up of "cells"
    - squares will be 0 | 1 | 2
                      3 | 4 | 5
                      6 | 7 | 8

The Rows, columns and squares
"""

grid = "006080900 309760800 040201007 930000000 081649230 000000089 100408090 002037501 003010700"
possible_values = list("123456789")
box_dict = {0: (0, 0), 1: (0, 3), 2: (0, 6),
            3: (3, 0), 4: (3, 3), 5: (3, 6),
            6: (6, 0), 7: (6, 3), 8: (6, 6)}


class Cell:
    """
    has an (x,y) coordinate, a value, and a list of possible values
    """

    def __init__(self, x_coord, y_coord, init_value):
        """

        :param x_coord: Lets the Cell know where it is on the X-coordinate for grouping purposes
        :param y_coord: Lets the Cell know where it is on the Y-coordinate for grouping purposes
        :param init_value: The Cell's (initial) value, left as 0 for an empty cell
        """
        self.value = init_value
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.legal_values = []  # A list of all legal values that could fill in this cell

        if self.value == "0":
            self.legal_values = list("123456789")

    def get_coords(self):
        """

        :return: the (x,y) position of the Cell
        """
        return self.x_coord, self.y_coord

    def update(self, illegal_values):
        """
        :param illegal_values: a list/string of values to be removed from consideration of potential values in the
        given Cell

        if after update is run there is only 1 remaining legal value the Cell will automatically fill itself in.
        """
        # for each item in the list of illegal values
        for item in illegal_values:
            # if that item is currently considered a possible legal value,
            if item in self.legal_values:
                # remove it from the list of legal values
                self.legal_values.remove(item)

        # If there is only one possible legal value
        if len(self.legal_values) == 1:
            # then fill in the cell with that value
            self.value = self.legal_values[0]

    def set(self, kept_values):
        """

        :param kept_values: a list of values you want to set as the only possible candidates for the Cell
        """
        nix = list("123456789")
        nix.remove(kept_values)
        self.update(nix)

    def __str__(self):
        return self.value


class Grid:
    def __init__(self, grid_values):
        """

        :param grid_values: a single string of the values in the grid, row by row, with each row separated with a SPACE.
        A list of strings is also acceptable. Do NOT make a list of lists, I will punch you.

        """
        self.grid_values = []

        self.grid = []  # List of Cell lists

        self.s_rows = []  # A list of rows with the solved values in that row

        self.s_cols = []  # A list of columns with the solved values in that column

        self.s_boxes = []  # A list of boxes with the solved values in that box

        if type(grid_values) == str:
            g_v = grid_values.split(" ")
            for i in range(9):
                g_v[i] = list(g_v[i])
            self.grid_values = g_v

        elif type(grid_values) == list and type(grid_values[0] == str):
            for i in range(9):
                grid_values[i] = list(grid_values[i])
            self.grid_values = grid_values
        # turns grid_values into a list of string lists

        else:
            print("I only accept a single string separated with spaces or a list of 9 strings.")
            raise TypeError
            #  if(type(grid_values)== list and type(grid_values[0])== list)
                #  print("Also, i'm punching you.")

        # populate the rows and columns of the sudoku puzzle with Cells
        for x in range(9):
            s_col = []
            row = []
            s_row = []
            for y in range(9):
                cell = Cell(x, y, self.grid_values[x][y])
                row.append(cell)
                s_row.append(self.grid_values[x][y])
                s_col.append(self.grid_values[y][x])

            self.grid.append(row)

            # creates a list of each unique solved value in that row
            s_row = list(set(s_row))
            # creates a list of each unique solved value in that column
            s_col = list(set(s_col))

            self.s_rows.append(s_row)
            self.s_cols.append(s_col)

        for x_base in range(0, 9, 3):
            for y_base in range(0, 9, 3):
                s_box = []
                for x in range(3):
                    for y in range(3):
                        s_box.append(self.grid_values[x_base + x][y_base + y])
                s_box = list(set(s_box))  # creates a list of each unique solved value in that box
                self.s_boxes.append(s_box)
        self.solve()

    def update(self):
        """
        updates the grid allowing the solved values for each row/col/box to be updated.
        """
        gr = ""
        for row in self.grid:
            for cell in row:
                gr += str(cell)
            gr += " "
        self.__init__(gr)

    def row_check(self, y_coord):
        """
        row_check() goes to each empty Cell in a given row, and removes already solved values from the list of legal
        values for that Cell. This process checks both the solved values of the Cell's row and column.
        :param y_coord: the y-coordinate of the row being checked. 

        """
        for i in range(9):
            if self.grid[y_coord][i].value == "0":
                illegal_values = self.s_rows[y_coord] + self.s_cols[i]
                self.grid[y_coord][i].update(list(set(illegal_values)))

    def box_check(self, box_num):
        """
        box_check() goes through each Cell in a certain box and removes the solved values from the list of legal values
        for that Cell
        :param box_num: the box's numerical identifier. Read from left to right, then top to bottom.

        """
        x, y = box_dict[box_num]
        for r in range(x, x + 3):
            for c in range(y, y + 3):
                if self.grid[r][c].value == "0":
                    illegal_values = list(set(self.s_boxes[box_num] + self.s_cols[c] + self.s_rows[r]))
                    self.grid[r][c].update(illegal_values)

    def box_forced_placement(self, box_num):
        """
        Goes through each Cell in a box and finds which potential values only appear once. Then it fills in the appropriate Cells.
        :param box_num: the box's ID number
        """
        x, y = box_dict[box_num]
        # All unsolved values within the box
        total_options = []
        # The unsolved values that are only found in one
        forced_options = []

        for r in range(x, x + 3):
            for c in range(y, y + 3):
                total_options += self.grid[r][c].legal_values

        for item in possible_values:
            if item in total_options:
                count = total_options.count(item)
                if count == 1:
                    forced_options.append(item)
                else:
                    # prevents the code from checking the same number multiple times.
                    total_options.remove(item)  # total_options = (e for e in total_options if e not in (item))

        if len(forced_options) > 0:
            for num in forced_options:
                for r in range(x, x + 3):
                    for c in range(y, y + 3):
                        if num in self.grid[r][c].legal_values:
                            self.grid[r][c].set(num)

    def row_forced_placement(self, row):
        """
        Goes through each Cell in a row and finds which values only appear once. Then it fills in the appropriate Cells.
        :param row: which row it's checking
        """
        total_options = []
        forced_options = []
        for i in range(9):
            total_options += self.grid[row][i].legal_values

        for item in possible_values:
            if item in total_options:
                count = total_options.count(item)
                if count == 1:
                    forced_options.append(item)
                else:
                    total_options.remove(item)

        if len(forced_options) > 0:
            for num in forced_options:
                for i in range(9):
                    if num in self.grid[row][i].legal_values:
                        self.grid[row][i].set(num)

    def col_forced_placement(self, col):
        """
        Goes through each Cell in a column and finds which values only appear once. Then it fills in the appropriate
        Cells.
        :param col: which column it's checking
        """
        total_options = []
        forced_options = []
        for i in range(9):
            total_options += self.grid[col][i].legal_values

        for item in possible_values:
            if item in total_options:
                count = total_options.count(item)
                if count == 1:
                    forced_options.append(item)
                else:
                    total_options.remove(item)

        if len(forced_options) > 0:
            for num in forced_options:
                for i in range(9):
                    if num in self.grid[col][i].legal_values:
                        self.grid[col][i].set(num)

    def locked_row(self, box_num):
        """
        Checks to see if there are any legal values in a box that only exist in a certain row, and removes them from
        other Cells in that same row.
        :param box_num:
        :return:
        """
        x, y = box_dict[box_num]
        for checking_row in range(x, x + 3):
            included = []
            excluded = []

            for r in range(x, x + 3):
                for c in range(y, y + 3):
                    if r == checking_row:
                        included += self.grid[r][c].legal_values
                    else:
                        excluded += self.grid[r][c].legal_values

            # Get rid of duplicate values to prevent unnecessary checks
            included = list(set(included))
            excluded = list(set(excluded))

            for option in included:
                # If the value is unique to the row...
                if option not in excluded:
                    # Going through the row...  
                    for i in range(9):
                        # ...Except for the box we're at...
                        if i not in range(y, y + 3):
                            # ...remove the option from the other Cells
                            self.grid[checking_row][i].update(option)

    def locked_col(self, box_num):
        """
        Checks to see if there are any legal values in a box that only exist in a certain column, and removes them from
        other Cells in that same column.
        :param box_num:
        :return:
        """
        x, y = box_dict[box_num]
        for checking_col in range(y, y + 3):
            included = []
            excluded = []

            for c in range(y, y + 3):
                for r in range(x, x + 3):
                    if c == checking_col:
                        included += self.grid[r][c].legal_values
                    else:
                        excluded += self.grid[r][c].legal_values
            # Get rid of duplicate values to prevent unnecessary checks
            included = list(set(included))
            excluded = list(set(excluded))

            for option in included:
                # if the value is unique to that column
                if option not in excluded:
                    # Going through the column...
                    for i in range(9):
                        # ...Except for the box we're at...
                        if i not in range(x, x + 3):
                            # ...remove the option from the other boxes
                            self.grid[i][checking_col].update(option)

    def naked_box_pair(self, box_num):
        """
        checks to see if two Cells both only have the same 2 legal values available to them. If they do, it removes
        those values as options from other Cells in the bow
        :param box_num: which box we're looking at
        """
        x, y = box_dict[box_num]
        cells = []
        for r in range(x, x + 3):
            for c in range(y, y + 3):
                # if there are only 2 possible options in a cell
                if len(self.grid[r][c].legal_values) == 2:
                    cells.append(self.grid[r][c])

        while len(cells) > 1:
            cell_a = cells.pop()
            for cell in cells:
                if cell.legal_values == cell_a.legal_values:
                    for r in range(x, x + 3):
                        for c in range(y, y + 3):
                            if cell.get_coords() != self.grid[r][c].get_coords() != cell_a.get_coords():
                                self.grid[r][c].update(cell.legal_values)

    def naked_col_pair(self, col):
        """
        checks to see if two Cells both only have the same 2 legal values available to them. If they do, it removes
        those values from other Cells in the column
        :param col: what column it's looking at.
        :return:
        """
        cells = []
        for r in range(9):
            if len(self.grid[r][col].legal_values) == 2:
                cells.append(self.grid[r][col])

        while len(cells) > 1:
            cell_a = cells.pop()
            for cell in cells:
                if cell.legal_values == cell_a.legal_values:
                    for r in range(9):
                        if cell.get_coords() != self.grid[r][col].get_coords() != cell_a.get_coords():
                            self.grid[r][col].update(cell.legal_values)

    def naked_row_pair(self, row):
        """
        checks to see if two Cells both only have the same 2 legal values available to them. If they do, it removes
        those values from other Cells in the row
        :param row: which row it's looking at
        :return:
        """
        cells = []
        for c in range(9):
            if len(self.grid[row][c].legal_values) == 2:
                cells.append(self.grid[row][c])

        while len(cells) > 1:
            cell_a = cells.pop()
            for cell in cells:
                if cell.legal_values == cell_a.legal_values:
                    for c in range(9):
                        if cell.get_coords() != self.grid[row][c].get_coords() != cell_a.get_coords():
                            self.grid[row][c].update(cell.legal_values)

    def hidden_row_pair(self, row):

        pass

    def compare_legal_values(self, cell_a, box_num):
        x, y = box_dict[box_num]
        x2, y2 = cell_a.get_coords()
        for r in range(x, x + 3):
            for c in range(y, y + 3):
                if x2 != r and y2 != c:
                    if len(self.grid[r][c].legal_values) == 2:
                        if cell_a.legal_values.sort() == self.grid[r][c].legal_values.sort():
                            return r, c
        return -1, -1

    def solve(self, recurred=False):
        """
        attempts to solve the sudoku puzzle. It will update the grid if it has gone through the cycle and a value has
        changed. If nothing changed, it will go through the cycle one more time, just in case the legal values changed
        allowed for something to be solved. If after the second pass there is still no change, or no empty cells remain,
        it will print out the grid in its current state.
        :param recurred:
        :return:
        """
        for i in range(9):
            self.box_check(i)
            self.box_forced_placement(i)

        for i in range(9):  # Due to how much boxes intersect with rows/cols it felt right to not do them together
            self.row_forced_placement(i)
            self.col_forced_placement(i)

        for i in range(9):
            self.locked_col(i)
            self.locked_row(i)

        for i in range(9):
            self.naked_box_pair(i)
            self.naked_col_pair(i)
            self.naked_row_pair(i)

        if self.is_solved():
            print(self.__str__())
        elif self.has_changed():
            self.update()
        else:
            if not recurred:
                self.solve(True)
            else:
                print(self.__str__())

    def is_solved(self):
        gr = ""
        for row in self.grid:
            for cell in row:
                gr += str(cell)
            gr += "\n"
        return "0" not in gr

    def has_changed(self):
        gr = ""
        for row in self.grid:
            for cell in row:
                gr += str(cell)
            gr += "\n"
        return self.__str__() != gr

    def __str__(self):
        g_v = []
        for row in self.grid_values:
            g_v.append("".join(row))
        return "\n".join(g_v)


g = Grid("009000602 100720009 003900000 400030060 000509000 010060003 000005200 500047008 908000300")
