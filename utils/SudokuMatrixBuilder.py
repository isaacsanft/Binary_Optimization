class SudokuMatrixBuilder:
    def __init__(self, header_node):
        self.header = header_node

    def create_column_headers(self, ColumnNodeClass):
        headers = []
        for i in range(1, 10):
            for j in range(1, 10):
                headers.append(ColumnNodeClass(f"P{i}{j}"))
        for k in range(1, 10):
            for l in range(1, 10):
                headers.append(ColumnNodeClass(f"R{k}V{l}"))
        for m in range(1, 10):
            for n in range(1, 10):
                headers.append(ColumnNodeClass(f"C{m}V{n}"))
        for o in range(1, 10):
            for p in range(1, 10):
                headers.append(ColumnNodeClass(f"B{o}V{p}"))

        for q in range(len(headers)):
            left = q - 1
            right = (q + 1) % len(headers)
            headers[q].left = headers[left]
            headers[q].right = headers[right]

        self.header.right = headers[0]
        headers[0].left = self.header
        self.header.left = headers[-1]
        headers[-1].right = self.header

        return headers

    def find_box(self, row, col):
        if (row // 3) == 0:
            return (col // 3) + 1
        elif (row // 3) == 1:
            return (col // 3) + 4
        elif (row // 3) == 2:
            return (col // 3) + 7

    def column_positions(self, row, col, value):
        constraint1 = 9 * (row - 1) + col - 1
        constraint2 = 9 * (row - 1) + value + 80
        constraint3 = 9 * (col - 1) + value + 161
        constraint4 = 9 * (self.find_box(row - 1, col - 1) - 1) + value + 242
        return [constraint1, constraint2, constraint3, constraint4]

    def add_node_to_column(self, node, column):
        node.up = column.up
        node.down = column
        column.up.down = node
        column.up = node
        column.size += 1
        node.column = column

    def link_row(self, nodes):
        nodes[0].right = nodes[1]
        nodes[1].left = nodes[0]
        nodes[1].right = nodes[2]
        nodes[2].left = nodes[1]
        nodes[2].right = nodes[3]
        nodes[3].left = nodes[2]
        nodes[3].right = nodes[0]
        nodes[0].left = nodes[3]

    def build_constraint_matrix(self, NodeClass, ColumnNodeClass):
        headers = self.create_column_headers(ColumnNodeClass)
        for row in range(1, 10):
            for col in range(1, 10):
                for val in range(1, 10):
                    positions = self.column_positions(row, col, val)
                    nodes = []
                    for l in range(4):
                        column = headers[positions[l]]
                        node = NodeClass()
                        node.row_id = (row, col, val)
                        self.add_node_to_column(node, column)
                        nodes.append(node)
                    self.link_row(nodes)
        return headers

    def given_values(self, grid):
        row_ids = []
        for row in range(9):
            for column in range(9):
                if grid[row][column] in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    row_ids.append((row + 1, column + 1, grid[row][column]))
        return row_ids

    def rowid_to_node(self, rowid, col_header):
        pointer = col_header
        for i in range(rowid[2]):
            pointer = pointer.down
        return pointer