import matplotlib.pyplot as plt
import numpy as np
from core.nodes import Node, ColumnNode
from core.Algorithms import Algorithm
from utils.SudokuMatrixBuilder import SudokuMatrixBuilder
import time

def draw_sudoku_board(sudoku, title_suffix):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    ax.set_xlim(0, 9)
    ax.set_ylim(9, 0)
    for i in range(0, 10, 3):
        ax.axvline(x=i, color='black', linewidth=3)
        ax.axhline(y=i, color='black', linewidth=3)
    for i in range(0, 10, 1):
        if i % 3 != 0:
            ax.axvline(x=i, color='gray', linestyle='-', linewidth=0.5)
            ax.axhline(y=i, color='gray', linestyle='-', linewidth=0.5)
    for i in range(9):
        for j in range(9):
            cell_value = sudoku[i][j]
            if cell_value != 0:
                ax.text(j + 0.5, i + 0.5, str(cell_value),
                        ha='center', va='center',
                        fontsize=24, color='darkblue',
                        fontweight='bold')
    fig.suptitle(f"Sudoku Board - {title_suffix}", fontsize=16, fontweight='bold', y=0.95)
    plt.show()

def main():
    sudoku2 = [
        [0, 0, 0, 0, 0, 0, 0, 1, 0],
        [4, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 5, 0, 4, 0, 7],
        [0, 0, 8, 0, 0, 0, 3, 0, 0],
        [0, 0, 1, 0, 9, 0, 0, 0, 0],
        [3, 0, 0, 4, 0, 0, 2, 0, 0],
        [0, 5, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 8, 0, 6, 0, 0, 0]
    ]

    draw_sudoku_board(sudoku2, "Unsolved")

    solver = Algorithm()
    builder = SudokuMatrixBuilder(solver.header)
    headers = builder.build_constraint_matrix(Node, ColumnNode)

    clues = builder.given_values(sudoku2)
    for entry in clues:
        col_index = 9 * (entry[0] - 1) + entry[1] - 1
        target_node = None
        curr = headers[col_index].down
        while curr != headers[col_index]:
            if curr.row_id == entry:
                target_node = curr
                break
            curr = curr.down

        if target_node:
            solver.cover(target_node.column)
            solver.current_solution.append(target_node.row_id)
            r_ptr = target_node.right
            while r_ptr != target_node:
                solver.cover(r_ptr.column)
                r_ptr = r_ptr.right

    start = time.time()
    success =  solver.search_x()
    end = time.time()
    if success == True:
        solved_grid = np.zeros((9, 9), dtype=int)
        for r, c, v in solver.current_solution:
            solved_grid[r - 1][c - 1] = v
        draw_sudoku_board(solved_grid, f"Solved in {end - start:.6f}")
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()