import numpy as np

class CircuitMatrixBuilder:
    def __init__(self, header_node):
        self.header = header_node

    def build_pcb_problem(self, grid_width, grid_height, catalog):
        n_cols = grid_width * grid_height
        rows = []
        placement_map = {}
        row_idx = 0

        for comp in catalog:
            name = comp["name"]
            shape = comp["shape"]
            color = comp["color"]

            for y in range(grid_height):
                for x in range(grid_width):
                    abs_coords = [(x + dx, y + dy) for dx, dy in shape]

                    if all(0 <= cx < grid_width and 0 <= cy < grid_height for cx, cy in abs_coords):
                        binary_row = np.zeros(n_cols, dtype=np.uint8)
                        for cx, cy in abs_coords:
                            col_idx = cy * grid_width + cx
                            binary_row[col_idx] = 1

                        rows.append(binary_row)
                        placement_map[row_idx] = (name, x, y, abs_coords, color)
                        row_idx += 1

        matrix = np.array(rows) if rows else np.empty((0, n_cols))
        return matrix, placement_map

    def build_linked_list(self, matrix, NodeClass, ColumnNodeClass):
        n_rows, n_cols = matrix.shape
        active_columns = np.where(matrix.sum(axis=0) > 0)[0]
        col_map = {old_idx: new_idx for new_idx, old_idx in enumerate(active_columns)}

        headers = [ColumnNodeClass(f"C{j}") for j in active_columns]

        for q in range(len(headers)):
            headers[q].left = headers[q - 1]
            headers[q].right = headers[(q + 1) % len(headers)]

        if headers:
            self.header.right = headers[0]
            headers[0].left = self.header
            self.header.left = headers[-1]
            headers[-1].right = self.header

        min_len = float('inf')
        for i in range(n_rows):
            row_nodes = []
            ones_in_row = np.where(matrix[i] == 1)[0]
            valid_ones = [idx for idx in ones_in_row if idx in col_map]

            if valid_ones:
                row_len = len(valid_ones)
                min_len = min(min_len, row_len)

                for col_idx in valid_ones:
                    col = headers[col_map[col_idx]]
                    node = NodeClass()
                    node.row_id = i
                    node.up = col.up
                    node.down = col
                    col.up.down = node
                    col.up = node
                    col.size += 1
                    node.column = col
                    row_nodes.append(node)

                for k in range(len(row_nodes)):
                    row_nodes[k].left = row_nodes[k - 1]
                    row_nodes[k].right = row_nodes[(k + 1) % len(row_nodes)]

        return headers, (min_len if min_len != float('inf') else 1)