import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from core.nodes import Node, ColumnNode
from core.Algorithms import Algorithm
from utils.SpectrumMatrixBuilder import SpectrumMatrixBuilder
import time

# --- CONFIGURATION PARAMETERS ---
GRID_SIZE = 40
N_SPOTS = 40
SIZE_MIN = 30
SIZE_MAX = 50
SEED = 42


# --------------------------------

def build_matrix(n_spots, grid_size, size_min, size_max, seed):
    rng = np.random.default_rng(seed)
    matrix = np.zeros((n_spots, grid_size * grid_size), dtype=np.uint8)
    spots, sizes = [], []
    rows_grid, cols_grid = np.arange(grid_size), np.arange(grid_size)
    rr, cc = np.meshgrid(rows_grid, cols_grid, indexing="ij")

    for i in range(n_spots):
        cr, cc_ = int(rng.integers(0, grid_size)), int(rng.integers(0, grid_size))
        n_cells = int(rng.integers(size_min, size_max + 1))
        spots.append((cr, cc_))
        sizes.append(n_cells)

        angle, aspect = rng.uniform(0, np.pi), rng.uniform(0.45, 0.92)
        a = np.sqrt(n_cells / (np.pi * aspect))
        b = aspect * a
        cos_t, sin_t = np.cos(angle), np.sin(angle)
        dr, dc = rr - cr, cc - cc_
        dr_rot, dc_rot = cos_t * dr + sin_t * dc, -sin_t * dr + cos_t * dc
        base_dist = np.sqrt((dr_rot / a) ** 2 + (dc_rot / b) ** 2)
        theta = np.arctan2(dc_rot, dr_rot)
        n_waves, phase, amplitude = rng.integers(2, 6), rng.uniform(0, 2 * np.pi), rng.uniform(0.14, 0.30)
        dist = base_dist / (1.0 + amplitude * np.sin(n_waves * theta + phase))
        chosen = np.argsort(dist.flatten())[:n_cells]
        matrix[i, chosen] = 1

    return matrix, spots, sizes


def visualize_matrix(matrix, spots, grid_size, title="Coverage"):
    coverage = matrix.sum(axis=0).reshape(grid_size, grid_size).astype(float)
    extent = (-0.5, grid_size - 0.5, grid_size - 0.5, -0.5)
    cmap = LinearSegmentedColormap.from_list("glow", ["#0d1117", "#0c2a3a", "#0e6b8a", "#06b6d4", "#67e8f9", "#f0f9ff"])

    fig, ax = plt.subplots(figsize=(9, 9))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    covered = coverage[coverage > 0]
    vmax = float(np.percentile(covered, 97)) if covered.size else 1.0
    ax.imshow(coverage, origin="upper", aspect="equal", interpolation="nearest", extent=extent, cmap=cmap, vmin=0,
              vmax=vmax)

    x_grid = np.arange(grid_size)
    y_grid = np.arange(grid_size)

    for i in range(matrix.shape[0]):
        if matrix[i].sum() > 0:
            mask = matrix[i].reshape(grid_size, grid_size).astype(float)
            ax.contour(x_grid, y_grid, mask, levels=[0.5],
                       colors=["#ff3333"], alpha=0.8, linewidths=0.8, zorder=3)

    if spots:
        sx, sy = [c for _, c in spots], [r for r, _ in spots]
        ax.scatter(sx, sy, c="#f0f9ff", s=22, marker="o", linewidths=0.6, edgecolors="#0e7490", zorder=5, alpha=0.9)

    ax.set_title(title, color="white", fontsize=12, fontfamily="monospace")
    plt.tight_layout()
    plt.show()


def solution_to_matrix(solution_ids, original_matrix):
    new_matrix = np.zeros_like(original_matrix)
    for row_idx in solution_ids:
        new_matrix[row_idx] = original_matrix[row_idx]
    return new_matrix


def main():
    raw_matrix, spots, sizes = build_matrix(N_SPOTS, GRID_SIZE, SIZE_MIN, SIZE_MAX, SEED)
    visualize_matrix(raw_matrix, spots, GRID_SIZE, "Original Overlap")

    # Max Coverage
    solver_cov = Algorithm()
    solver_cov.best_coverage = -1
    builder_cov = SpectrumMatrixBuilder(solver_cov.header)
    headers_cov, _ = builder_cov.build_from_numpy(raw_matrix, Node, ColumnNode)
    solver_cov.feasible_count = len(headers_cov)

    print(f"Solving Max Coverage for {N_SPOTS} spots on {GRID_SIZE}x{GRID_SIZE} grid...")
    start = time.time()
    solver_cov.search_uf_cover()
    end = time.time()

    if solver_cov.best_solution:
        res_cov = solution_to_matrix(solver_cov.best_solution, raw_matrix)
        visualize_matrix(res_cov, [spots[i] for i in solver_cov.best_solution], GRID_SIZE,
                         f"Max Coverage Result in {end - start:.4f}s")
    else:
        print("No coverage solution found.")

    # Max Density
    solver_den = Algorithm()
    solver_den.best_density = -1
    builder_den = SpectrumMatrixBuilder(solver_den.header)
    headers_den, min_r = builder_den.build_from_numpy(raw_matrix, Node, ColumnNode)
    solver_den.feasible_count = len(headers_den)
    solver_den.min_row_length = min_r if min_r > 0 else 1

    print(f"Solving Max Density for {N_SPOTS} spots...")
    start_den = time.time()
    solver_den.search_uf_density()
    end_den = time.time()

    if solver_den.best_solution:
        res_den = solution_to_matrix(solver_den.best_solution, raw_matrix)
        visualize_matrix(res_den, [spots[i] for i in solver_den.best_solution], GRID_SIZE,
                         f"Max Density Result in {end_den - start_den:.4f}s")
    else:
        print("No density solution found.")


if __name__ == "__main__":
    main()