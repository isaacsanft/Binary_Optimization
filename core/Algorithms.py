from core.nodes import ColumnNode


class Algorithm:
    def __init__(self):
        self.header = ColumnNode("H")
        self.current_solution = []
        self.current_coverage = 0
        self.best_solution = []
        self.best_coverage = -1
        self.feasible_count = 0
        self.current_density = 0
        self.best_density = -1
        self.min_row_length = 0

    def cover(self, column):
        if column.size > 0:
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

    def uncover(self, column):
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
        if column.size > 0:
            self.feasible_count += 1

    def choose_column(self):
        best_col = None
        min_size = float('inf')
        curr = self.header.right
        while curr != self.header:
            if 0 < curr.size < min_size:
                min_size = curr.size
                best_col = curr
            curr = curr.right
        return best_col

    def search_x(self):
        if self.header.right == self.header:
            return True
        column = self.choose_column()
        if column is None:
            return False
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

            col_pointer = col_pointer.down

        self.uncover(column)
        return False

    def length_row(self, row_start):
        count = 1
        curr = row_start.right
        while curr != row_start:
            count += 1
            curr = curr.right
        return count

    def search_uf_cover(self):
        if self.feasible_count + self.current_coverage <= self.best_coverage:
            return
        if self.header.right == self.header:
            if self.current_coverage > self.best_coverage:
                self.best_coverage = self.current_coverage
                self.best_solution = self.current_solution.copy()
            return
        column = self.choose_column()
        if column is None:
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

            col_pointer = col_pointer.down

        self.uncover(column)
        return

    def search_uf_density(self):
        if (self.feasible_count // self.min_row_length) + self.current_density <= self.best_density:
            return
        if self.header.right == self.header:
            if self.current_density > self.best_density:
                self.best_density = self.current_density
                self.best_solution = self.current_solution.copy()
            return
        column = self.choose_column()
        if column is None:
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

            col_pointer = col_pointer.down

        self.uncover(column)
        return