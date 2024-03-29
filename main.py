"""
Sudoku Solver
reads in a 9x9 sudoku square with blanks filled in as '0'
separates the puzzle into 9 rows, 9 columns, and 9 3x3 squares
rows, columns, and squares will be made up of Cell objects
    - squares will be 0 | 1 | 2
                      3 | 4 | 5
                      6 | 7 | 8
"""

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
        :param x_coord: int
            Lets the Cell know where it is on the X-axis for grouping purposes
        :param y_coord: int
            Lets the Cell know where it is on the Y-axis for grouping purposes
        :param init_value: str
            The Cell's (initial) value, left as 0 for an empty cell
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
        
        # removes the items in illegal values from the Cell's legal values 
        self.legal_values = [e for e in self.legal_values if e not in illegal_values]      

        # If there is only one possible legal value
        if len(self.legal_values) == 1:
            # then fill in the cell with that value
            self.value = self.legal_values[0]

    def set(self, kept_values):
        """
        :param kept_values: a value or list of values you want to set as the only possible candidates for the Cell
        """
        nix = list("123456789")
        nix = [num for num in nix if num not in kept_values]
        self.update(nix)

    def __str__(self):
        return self.value


class Grid:
    def __init__(self, grid_values):
        """
        :param grid_values: a single string of the values in the grid, row by row, top to bottom, with each row separated with a SPACE.
        A list of strings is also acceptable.

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
            if('0' in s_row):
                s_row.remove('0')
            # creates a list of each unique solved value in that column
            s_col = list(set(s_col))
            if('0' in s_col):
                s_col.remove('0')

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
        updates the grid allowing the solved values for each row/column/box to be updated.
        """
        gr = ""
        for row in self.grid:
            for cell in row:
                gr += str(cell)
            gr += " "
        self.__init__(gr)

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
        x,y = box_dict[box_num]
        value_locations = {}
        # prevents solved values from being checked unnecessarily
        unsolved_values = [e for e in possible_values if e not in self.s_boxes[box_num]] 
        # make a dictionary of all Cells an unsolved value is legal in
        for val in unsolved_values:
            legal_cells = []
            for r in range(x, x+3):
                for c in range(y, y+3):
                    if val in self.grid[r][c].legal_values:
                        legal_cells.append((r,c))
            
            value_locations[val]=legal_cells

        # set values that only appear once in the appropriate Cell
        for val in unsolved_values:  
            if len(value_locations[val]) == 1:
                r,c = value_locations[val][0]
                self.grid[r][c].set(val)

    def row_forced_placement(self, row):
        """
        Goes through each Cell in a row and finds which values only appear once. Then it fills in the appropriate Cells.
        :param row: which row it's checking
        """
        value_locations = {}
        
        unsolved_values = [e for e in possible_values if e not in self.s_rows[row]]
        # make a dictionary of all cells a value is legal in
        for i in unsolved_values:
            legal_cells = []
            for y in range(9):
                if i in self.grid[row][y].legal_values:
                    legal_cells.append(y)
            value_locations[i]=legal_cells

        # set values that only appear once in the appropriate Cell
        for i in unsolved_values:  
            if len(value_locations[i]) == 1:
                y = value_locations[i][0]
                self.grid[row][y].set(i)

    def col_forced_placement(self, col):
        """
        Goes through each Cell in a column and finds which values only appear once. Then it fills in the appropriate
        Cells.
        :param col: which column it's checking
        """
        value_locations = {}
  
        unsolved_values = [e for e in possible_values if e not in self.s_cols[col]]
        # make a dictionary of all cells a value is legal in
        for i in unsolved_values:
            legal_cells = []
            for x in range(9):
                if i in self.grid[x][col].legal_values:
                    legal_cells.append(x)
            value_locations[i]=legal_cells

       # set values that only appear once in the appropriate Cell
        for i in unsolved_values:  
            if len(value_locations[i]) == 1:
                x = value_locations[i][0]
                self.grid[x][col].set(i)

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
        those values as options from other Cells in the box
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
            if len(self.grid[row][c].legal_values) == 2: #  if the cell only has 2 legal values
                cells.append(self.grid[row][c])  #  add it to the list

        while len(cells) > 1: #  while there's still cells to compare to
            cell_a = cells.pop() #  remove a cell the list
            for cell in cells: #  check it against the remaining cells
                if cell.legal_values == cell_a.legal_values: #  if they have matching legal values
                    for c in range(9):
                        if cell.get_coords() != self.grid[row][c].get_coords() != cell_a.get_coords(): # except for the cells we're looking at
                            self.grid[row][c].update(cell.legal_values) #  remove those legal values from all other cells in the row

    def hidden_box_pair(self, box_num):
        """
        checks to see if a pair of numbers are only available in two cells in a given box and removes all other legal values from the cell.
        :param box_num: which box we're looking at
        """
        x,y = box_dict[box_num]
        value_locations = {}
        hidden_options = []
        # prevents solved values from being checked unnecessarily
        unsolved_values = [e for e in possible_values if e not in self.s_boxes[box_num]] 
        # make a dictionary of all cells an unsolved value is legal in
        for i in unsolved_values:
            legal_cells = []
            for r in range(x, x+3):
                for c in range(y, y+3):
                    if i in self.grid[r][c].legal_values:
                        legal_cells.append((r,c))
            value_locations[i]=legal_cells

        # make a list of all values that only appear twice
        for i in unsolved_values:  
            if len(value_locations[i]) == 2:
                hidden_options.append(i)
        
        # check if those values appear in the same two cells
        while len(hidden_options) >= 2:
            value_a = hidden_options.pop()
            rem_val = "0"
            for val in hidden_options:
                if value_locations[value_a] == value_locations[val]:
                    # if they do remove all other values from those cells
                    rem_val = val # remember which value matched to remove it
                    for r,c in value_locations[val]:
                        self.grid[r][c].set([val, value_a])
                break
            if rem_val !="0": 
                hidden_options.remove(rem_val) #  remove matching value to avoid extra loops  

    def hidden_row_pair(self, row):
        """
        checks to see if a pair of numbers are only available in two cells in a given row and removes all other legal values from the cell.
        :param row: which row we're looking at
        """
        
        value_locations = {}
        hidden_options = []
        unsolved_values = [e for e in possible_values if e not in self.s_rows[row]]
        # make a dictionary of all cells a value is legal in
        for i in unsolved_values:
            legal_cells = []
            for y in range(9):
                if i in self.grid[row][y].legal_values:
                    legal_cells.append(y)
            value_locations[i]=legal_cells

        # make a list of all values that only appear twice
        for i in unsolved_values:  
            if len(value_locations[i]) == 2:
                hidden_options.append(i)
        
        x_wing_values = hidden_options.copy() # i probably could've just called the method first but it feels... rude(?) not to let it finish first
        

        # check if those values appear in the same two cells
        while len(hidden_options) >= 2:
            value_a = hidden_options.pop()
            rem_val = "0"
            for val in hidden_options:
                if value_locations[value_a] == value_locations[val]:
                    # if they do remove all other values from those cells
                    rem_val = val # remember which value matched to remove it
                    for y in value_locations[val]:
                        self.grid[row][y].set([val, value_a])
                break
            if rem_val !="0":
                hidden_options.remove(rem_val) #  remove matching value to avoid extra loops
        
        self.x_wing_check_row(x_wing_values, row, value_locations)
        
    def x_wing_check_row(self, values, starting_row, value_locations):
        """
        if there is a hidden pair, check other rows to see if there is an x-wing pattern
        :param values: the values in the hidden pair to look for in other rows
        :param starting_row: the initial row 
        :param value_locations: holds the potential y coords of each value in the starting row
        """
        # bonus: check to see how many times the values appear in the column? see if this whole process is even worth doing?
        for value in values:
            y1, y2 = value_locations[value]
            for row in range(9):
                # if this row is the row we started at, or has solved the value, skip it
                if row==starting_row or value in self.s_rows[row]:
                    continue
                else:
                    skip_row = False
                    # check to see if the value is a legal value at both y positions in the row
                    if value in self.grid[row][y1].legal_values and value in self.grid[row][y2].legal_values:
                    # check to make sure value doesnt appear outside of those y positions
                        for i in range(9):
                            if i not in [y1, y2] and value in self.grid[row][i].legal_values:
                                skip_row=True
                                break
                        if skip_row:
                            continue
                        # if they don't, remove the value as a legal option from all other rows except the starting row and the matching row
                        else: 
                            for i in range(9):
                                if i not in [row, starting_row]:
                                    self.grid[i][y1].update(value)
                                    self.grid[i][y2].update(value)
    
    def hidden_col_pair(self, col):
        """
        checks to see if a pair of numbers are only available in two cells in a given col and removes all other legal values from the cell.
        :param col: which column we're looking at
        """
        
        value_locations = {}
        hidden_options = []
        unsolved_values = [e for e in possible_values if e not in self.s_cols[col]]
        # make a dictionary of all cells a value is legal in
        for i in unsolved_values:
            legal_cells = []
            for x in range(9):
                if i in self.grid[x][col].legal_values:
                    legal_cells.append(x)
            value_locations[i]=legal_cells

        # make a list of all values that only appear twice
        for i in unsolved_values:  
            if len(value_locations[i]) == 2:
                hidden_options.append(i)
        
        x_wing_values = hidden_options.copy()

        # check if those values appear in the same two cells
        while len(hidden_options) >= 2:
            value_a = hidden_options.pop()
            rem_val = "0"
            for val in hidden_options:
                if value_locations[value_a] == value_locations[val]:
                    # if they do remove all other values from those cells
                    rem_val = val # remember which value matched to remove it
                    for x in value_locations[val]:
                        self.grid[x][col].set([val, value_a])
                break
            if rem_val !="0":
                hidden_options.remove(rem_val) #  remove matching value to avoid extra loops        
        self.x_wing_check_col(x_wing_values, col, value_locations)

    def x_wing_check_col(self, values, starting_col, value_locations):
        """
        if there is a hidden pair, check other columns to see if there is an x-wing pattern
        :param values: the values in the hidden pair to look for in other columns
        :param starting_col: the initial column
        :param value_locations: holds the potential y coords of each value in the starting column
        """
        # bonus: check to see how many times the values appear in the row? see if this whole process is even worth doing?
        for value in values:
            x1, x2 = value_locations[value]
            for col in range(9):
                # if this column is the column we started at, or has solved the value, skip it
                if col==starting_col or value in self.s_cols[col]:
                    continue
                else:
                    skip_col = False
                    # check to see if the value is a legal value at both x positions in the column
                    if value in self.grid[x1][col].legal_values and value in self.grid[x2][col].legal_values:
                    # check to make sure value doesnt appear outside of those x positions
                        for i in range(9):
                            if i not in [x1, x2] and value in self.grid[i][col].legal_values:
                                skip_col=True
                                break
                        if skip_col:
                            continue
                        # if they don't, remove the value as a legal option from all other columns except the starting column and the matching column
                        else: 
                            for i in range(9):
                                if i not in [col, starting_col]:
                                    self.grid[x1][i].update(value)
                                    self.grid[x2][i].update(value)

    def solve(self, recurred=False):
        """
        attempts to solve the sudoku puzzle. It will update the grid if it has gone through the cycle and a value has
        changed. If nothing changed, it will go through the cycle one more time, just in case the changed legal values
        allowed for something to be solved. If after the second pass there is still no change, or no empty cells remain,
        it will print out the grid in its current state.
        :param recurred:
        """
  
        if self.is_solved():
            print("It is done: \n")
            print(self.formatted_grid())
            return

        #forced placement(box)
        for i in range(9):
            self.box_check(i)
            if not len(self.s_boxes[i])==9:
                self.box_forced_placement(i)
        
        #forced placement(row/col)
        for i in range(9):  # Due to how much boxes intersect with rows/cols it felt right to not do them together
            if not len(self.s_rows[i])==9:
                self.row_forced_placement(i)
            if not len(self.s_cols[i])==9:
                self.col_forced_placement(i)

        #locked pairs
        for i in range(9):
            if not len(self.s_cols[i])==9: #skips completely solved columns
                self.locked_col(i)
            if not len(self.s_rows[i])==9:
                self.locked_row(i)

        # naked pairs
        for i in range(9):
            if not len(self.s_boxes[i])==9:
                self.naked_box_pair(i)
            if not len(self.s_cols[i])==9:
                self.naked_col_pair(i)
            if not len(self.s_rows[i])==9:
                self.naked_row_pair(i)
        
        # hidden pairs
        for i in range(9):
            if not len(self.s_boxes[i])==9:
                self.hidden_box_pair(i)
            if not len(self.s_cols[i])==9:
                self.hidden_col_pair(i)
            if not len(self.s_rows[i])==9:
                self.hidden_row_pair(i)
        
        if self.has_changed():
            self.update()
        else:
            if not recurred:
                self.solve(True)
            else:
                print("I got stuck somewhere, this is the best i got.")
                print(self.formatted_grid())

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
    
    def formatted_grid(self):
        g_v = []
        for i in range(9):
            row = self.grid_values[i]
            row.insert(6, "|")
            row.insert(3, "|")
            g_v.append("".join(row))
            if i == 2 or i == 5:
                g_v.append("-----------")
        
        return "\n".join(g_v)
    
    def __str__(self):
        g_v = []
        for row in self.grid_values:
            g_v.append("".join(row))
        return "\n".join(g_v)


grid0 = "000000000 018049000 950073860 600000980 500010003 074000006 097320045 000490120 000000000"
grid1 = "006080900 309760800 040201007 930000000 081649230 000000089 100408090 002037501 003010700"
grid2 = "108530600 020001000 040000008 805003009 004000000 000090200 309005002 000600070 010000000"
prompt = "Please enter a solvable sudoku grid, row by row, with a space between each row and a 0 to represent an empty square:"
input_grid = input(f"{prompt}\n (e.g. {grid1})\n").strip()

g = Grid(input_grid)
