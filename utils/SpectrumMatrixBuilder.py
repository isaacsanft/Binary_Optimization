import numpy as np
from core.nodes import Node, ColumnNode


class SpectrumMatrixBuilder:
    def __init__(self, header_node):
        self.header = header_node

    def build_from_numpy(self, matrix, NodeClass, ColumnNodeClass):
        n_rows, n_cols = matrix.shape

        active_columns = np.where(matrix.sum(axis=0) > 0)[0]
        col_map = {old_idx: new_idx for new_idx, old_idx in enumerate(active_columns)}

        headers = []
        for j in active_columns:
            headers.append(ColumnNodeClass(f"C{j}"))

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