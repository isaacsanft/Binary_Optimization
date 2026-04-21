from core.nodes import ColumnNode


class Algorithm:
    def __init__(self):
        self.header = ColumnNode("H")  # Header pointer which points to the first column in the matrix. Acts as starting point.
        self.current_solution = []
        self.current_coverage = 0
        self.best_solution = []
        self.best_coverage = 0
        self.feasible_count = 0
        self.current_density = 0
        self.best_density = 0
        self.min_row_length = 0

    def cover(self, column): #Cover function. This is modifies our matrix, "covering" the rows and columns by disconnecting their neighbors from them (but not disconnect them from their neighbors -- this is important)
        self.feasible_count -= 1
        column.right.left = column.left
        column.left.right = column.right
        col_pointer = column.down
        while col_pointer != column:
            row_pointer = col_pointer.right
            while row_pointer != col_pointer:
                row_pointer.up.down = row_pointer.down
                row_pointer.down.up = row_pointer.up
                row_pointer.column.size -= 1
                if row_pointer.column.size == 0:
                    self.feasible_count -= 1
                row_pointer = row_pointer.right
            col_pointer = col_pointer.down

    def uncover(self, column): #This undoes the cover function. It's used to backtrack when the algorithm runs into a contradiction. Because the deleted nodes still point to their old neighbers, reinsertion is easy and efficient.
        col_pointer = column.up
        while col_pointer != column:
            row_pointer = col_pointer.left
            while row_pointer != col_pointer:
                row_pointer.up.down = row_pointer
                row_pointer.down.up = row_pointer
                if row_pointer.column.size == 0:
                    self.feasible_count += 1
                row_pointer.column.size += 1
                row_pointer = row_pointer.left
            col_pointer = col_pointer.up
        column.right.left = column
        column.left.right = column
        self.feasible_count += 1

    ### Algorithm X - Exact Cover ###

    def choose_column(self): #Deterministically choose column with the smallest size.
        count = 1000
        position = None
        pointer = self.header.right
        while pointer != self.header:
            if pointer.size < count:
                count = pointer.size
                position = pointer
            pointer = pointer.right
        return position

    def search_x(self): # The main algorithm X function. Essentially acts as a pre-order depth-first tree search where each level is another "cover" of the matrix. Backtracks when the child node is not the solution.
                      # If it finds a solution, returns true. If it traverses the whole tree and doesn't find a solution, returns false.
        if self.header.right == self.header:
            return True
        column = self.choose_column()
        self.cover(column)
        col_pointer = column.down
        while col_pointer != column:
            self.current_solution.append(col_pointer.row_id)
            row_pointer = col_pointer.right
            while row_pointer != col_pointer:
                self.cover(row_pointer.column)
                row_pointer = row_pointer.right
            if self.search_x():
                return True
            self.current_solution.pop()
            row_reverse_pointer = col_pointer.left
            while row_reverse_pointer != col_pointer:
                self.uncover(row_reverse_pointer.column)
                row_reverse_pointer = row_reverse_pointer.left
        self.uncover(column)
        return False

    ### Max Coverage Underfit Algorithm ###

    def length_row(self, row_start):
        count = 1
        curr = row_start.right
        while curr != row_start:
            count += 1
            curr = curr.right
        return count

    def search_uf_cover(self): # This algorithms finds the underfit (no overlap) that covers the most area
        if self.feasible_count + self.current_coverage <= self.best_coverage:
            return
        if self.header.right == self.header:
            if self.current_coverage > self.best_coverage:
                self.best_coverage = self.current_coverage
                self.best_solution = self.current_solution.copy()
            return
        column = self.choose_column()
        if column.size == 0:
            if self.current_coverage > self.best_coverage:
                self.best_coverage = self.current_coverage
                self.best_solution = self.current_solution.copy()
                return
        self.cover(column)
        col_pointer = column.down
        while col_pointer != column:
            self.current_solution.append(col_pointer.row_id)
            self.current_coverage += self.length_row(col_pointer)
            row_pointer = col_pointer.right
            while row_pointer != col_pointer:
                self.cover(row_pointer.column)
                row_pointer = row_pointer.right
            self.search_uf_cover()
            self.current_solution.pop()
            self.current_coverage -= self.length_row(col_pointer)
            row_reverse_pointer = col_pointer.left
            while row_reverse_pointer != col_pointer:
                self.uncover(row_reverse_pointer.column)
                row_reverse_pointer = row_reverse_pointer.left
        self.uncover(column)
        return

    ### Max Coverage Underfit Algorithm ###

    def search_uf_density(self): # This algorithms finds the underfit (no overlap) that covers with the highest number of rows (max density)
        if (self.feasible_count//self.min_row_length) + self.current_density <= self.best_density:
            return
        if self.header.right == self.header:
            if self.current_density > self.best_density:
                self.best_density = self.current_density
                self.best_solution = self.current_solution.copy()
            return
        column = self.choose_column()
        if column.size == 0:
            if self.current_density > self.best_density:
                self.best_density = self.current_density
                self.best_solution = self.current_solution.copy()
            return
        self.cover(column)
        col_pointer = column.down
        while col_pointer != column:
            self.current_solution.append(col_pointer.row_id)
            self.current_density += 1
            row_pointer = col_pointer.right
            while row_pointer != col_pointer:
                self.cover(row_pointer.column)
                row_pointer = row_pointer.right
            self.search_uf_density()
            self.current_solution.pop()
            self.current_density -= 1
            row_reverse_pointer = col_pointer.left
            while row_reverse_pointer != col_pointer:
                self.uncover(row_reverse_pointer.column)
                row_reverse_pointer = row_reverse_pointer.left
        self.uncover(column)
        return