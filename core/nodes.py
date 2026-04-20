class Node: #Create node class, including pointers to neighbor nodes, column header, and row id.
    def __init__(self):
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.column = None
        self.row_id = None

class ColumnNode(Node): #Create ColumnNode class that inherits from node class. Adds name and size attributes.
    def __init__(self, name):
        super().__init__()
        self.size = 0
        self.name = name
        self.column = self