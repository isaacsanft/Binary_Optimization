import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time

from core.nodes import Node, ColumnNode
from core.Algorithms import Algorithm
from utils.CircuitMatrixBuilder import CircuitMatrixBuilder

CATALOG = [
    {"name": "CPU", "color": "#4b5563", "shape": [(x, y) for x in range(4) for y in range(4)]},
    {"name": "GPU", "color": "#1f2937", "shape": [(x, y) for x in range(3) for y in range(3)]},
    {"name": "RAM", "color": "#047857", "shape": [(x, y) for x in range(1) for y in range(4)]},
    {"name": "GATE", "color": "#b45309", "shape": [(0, 0), (1, 0), (0, 1)]},
    {"name": "CAP", "color": "#1d4ed8", "shape": [(0, 0), (1, 0)]}
]

GRID_W = 12
GRID_H = 12


def visualize_pcb(solution_ids, placement_map, width, height, title):
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#022c22')
    ax.set_facecolor('#022c22')

    for x in range(width + 1):
        ax.axvline(x, color='#065f46', linewidth=1, zorder=0)
    for y in range(height + 1):
        ax.axhline(y, color='#065f46', linewidth=1, zorder=0)

    for row_id in solution_ids:
        name, basex, basey, coords, color = placement_map[row_id]

        min_x = min(c[0] for c in coords)
        max_x = max(c[0] for c in coords)
        min_y = min(c[1] for c in coords)
        max_y = max(c[1] for c in coords)

        for (cx, cy) in coords:
            rect = patches.Rectangle((cx + 0.05, cy + 0.05), 0.9, 0.9,
                                     linewidth=1, edgecolor='#fbbf24', facecolor=color, zorder=2)
            ax.add_patch(rect)

        center_x = min_x + (max_x - min_x + 1) / 2
        center_y = min_y + (max_y - min_y + 1) / 2
        ax.text(center_x, center_y, name, color="white", fontsize=8,
                ha='center', va='center', fontweight='bold', zorder=3)

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect('equal')
    ax.invert_yaxis()
    ax.set_title(title, color="#fbbf24", fontsize=14, fontfamily="monospace", pad=20)
    ax.axis('off')
    plt.tight_layout()
    plt.show()


def main():
    print(f"Building PCB Matrix for {GRID_W}x{GRID_H} board...")
    builder = CircuitMatrixBuilder(ColumnNode("H"))
    raw_matrix, placement_map = builder.build_pcb_problem(GRID_W, GRID_H, CATALOG)

    print(f"Matrix generated: {raw_matrix.shape[0]} valid component placements.\n")

    solver_cov = Algorithm()
    solver_cov.best_coverage = -1
    builder_cov = CircuitMatrixBuilder(solver_cov.header)
    headers_cov, _ = builder_cov.build_linked_list(raw_matrix, Node, ColumnNode)
    solver_cov.feasible_count = len(headers_cov)

    solver_cov.row_sizes = {i: raw_matrix[i].sum() for i in range(raw_matrix.shape[0])}

    print("Routing for Max Coverage...")
    start = time.time()
    solver_cov.search_uf_cover()
    end = time.time()

    if solver_cov.best_solution:
        print(f"Found area-optimal layout in {end - start:.4f}s")
        visualize_pcb(solver_cov.best_solution, placement_map, GRID_W, GRID_H,
                      f"Max Area Coverage ({solver_cov.best_coverage} cells)")

    solver_den = Algorithm()
    solver_den.best_density = -1
    builder_den = CircuitMatrixBuilder(solver_den.header)
    headers_den, min_r = builder_den.build_linked_list(raw_matrix, Node, ColumnNode)
    solver_den.feasible_count = len(headers_den)
    solver_den.min_row_length = min_r if min_r > 0 else 1

    solver_den.row_sizes = {i: raw_matrix[i].sum() for i in range(raw_matrix.shape[0])}

    print("\nRouting for Max Density...")
    start_den = time.time()
    solver_den.search_uf_density()
    end_den = time.time()

    if solver_den.best_solution:
        print(f"Found component-optimal layout in {end_den - start_den:.4f}s")
        visualize_pcb(solver_den.best_solution, placement_map, GRID_W, GRID_H,
                      f"Max Component Density ({solver_den.best_density} items)")


if __name__ == "__main__":
    main()