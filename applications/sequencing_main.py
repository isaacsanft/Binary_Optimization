import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from utils.SequencingMatrixBuilder import build_sequencing_matrix
from core.nodes import Node, ColumnNode
from core.Algorithms import Algorithm
from utils.SpectrumMatrixBuilder import SpectrumMatrixBuilder
import time

DOMAIN_LENGTH = 48
N_INTERVALS = 60
MIN_LEN = 2
MAX_LEN = 8
SEED = 46


def visualize_intervals(matrix, intervals, domain_length,
                        cov_solution=None, den_solution=None,
                        cov_coverage=0, cov_density=0,
                        den_coverage=0, den_density=0):

    n_intervals = len(intervals)
    sorted_indices = list(range(n_intervals))

    cov_set = set(cov_solution) if cov_solution else set()
    den_set = set(den_solution) if den_solution else set()
    positions = np.arange(domain_length)

    all_depth = matrix.sum(axis=0).astype(float)
    cov_depth = matrix[list(cov_set)].sum(axis=0).astype(float) if cov_set else np.zeros(domain_length)
    den_depth = matrix[list(den_set)].sum(axis=0).astype(float) if den_set else np.zeros(domain_length)

    BG         = "#0d1117"
    PANEL_BG   = "#0f1923"
    GRID_COL   = "#1a2535"
    TEXT_COL   = "#7a8fa6"
    COLOR_ALL  = "#1e3f5a"
    COLOR_COV  = "#06b6d4"
    COLOR_DEN  = "#f97316"
    COLOR_FADE = "#141e2e"

    titles = [
        "All Intervals",
        f"Max Coverage  ·  {cov_coverage} units  ·  {cov_density} intervals",
        f"Max Density   ·  {den_coverage} units  ·  {den_density} intervals",
    ]
    solution_sets  = [None, cov_set, den_set]
    active_colors  = [COLOR_ALL, COLOR_COV, COLOR_DEN]
    depths         = [all_depth, cov_depth, den_depth]
    depth_max      = all_depth.max() * 1.15 if all_depth.max() > 0 else 1.0

    fig = plt.figure(figsize=(21, 11))
    fig.patch.set_facecolor(BG)
    gs = gridspec.GridSpec(2, 3, figure=fig, height_ratios=[3.5, 1],
                           hspace=0.06, wspace=0.10,
                           left=0.06, right=0.97, top=0.91, bottom=0.08)

    for col_idx in range(3):
        ax_r = fig.add_subplot(gs[0, col_idx])
        ax_d = fig.add_subplot(gs[1, col_idx])

        for ax in (ax_r, ax_d):
            ax.set_facecolor(PANEL_BG)
            for spine in ax.spines.values():
                spine.set_edgecolor(GRID_COL)
            ax.tick_params(colors=TEXT_COL, labelsize=7.5)

        sol_set = solution_sets[col_idx]
        a_color = active_colors[col_idx]

        for y_pos, orig_idx in enumerate(sorted_indices):
            start, end = intervals[orig_idx]
            width = end - start

            if col_idx == 0:
                color, alpha = COLOR_ALL, 0.55
            elif orig_idx in sol_set:
                color, alpha = a_color, 0.92
            else:
                color, alpha = COLOR_FADE, 0.9

            ax_r.barh(y_pos, width, left=start, height=0.45,
                      color=color, alpha=alpha, linewidth=0)

        ax_r.set_xlim(0, domain_length)
        ax_r.set_ylim(-0.8, n_intervals - 0.2)
        ax_r.set_xticklabels([])
        ax_r.set_title(titles[col_idx], color="white", fontsize=8.5,
                       pad=7, fontfamily="monospace")
        if col_idx == 0:
            ax_r.set_ylabel("Interval Index", color=TEXT_COL, fontsize=8)
        ax_r.set_yticks([])

        ax_d.fill_between(positions, depths[col_idx],
                          color=a_color, alpha=0.55, step="mid")
        ax_d.step(positions, depths[col_idx], where="mid",
                  color=a_color, alpha=0.9, linewidth=0.9)
        ax_d.set_xlim(0, domain_length)
        ax_d.set_ylim(0, depth_max)
        ax_d.set_xlabel("Position (units)", color=TEXT_COL, fontsize=8)
        if col_idx == 0:
            ax_d.set_ylabel("Depth", color=TEXT_COL, fontsize=8)
        else:
            ax_d.set_yticklabels([])

        for x in np.linspace(0, domain_length, 11)[1:-1]:
            ax_r.axvline(x, color=GRID_COL, linewidth=0.4, alpha=0.6)
            ax_d.axvline(x, color=GRID_COL, linewidth=0.4, alpha=0.6)

    fig.suptitle(
        f"1D Interval Packing  ·  {domain_length} length  ·  {n_intervals} intervals  ·  Underfit Exact Cover",
        color="white", fontsize=12, fontfamily="monospace", y=0.965,
    )

    plt.show()


def main():
    matrix, intervals = build_sequencing_matrix(N_INTERVALS, DOMAIN_LENGTH, MIN_LEN, MAX_LEN, SEED)
    row_sizes = {i: int(matrix[i].sum()) for i in range(N_INTERVALS)}

    print(f"Matrix: {matrix.shape}  |  Domain: {DOMAIN_LENGTH} units  |  Intervals: {N_INTERVALS}")

    solver_cov = Algorithm()
    solver_cov.best_coverage = -1
    builder_cov = SpectrumMatrixBuilder(solver_cov.header)
    headers_cov, _ = builder_cov.build_from_numpy(matrix, Node, ColumnNode)
    solver_cov.feasible_count = len(headers_cov)
    solver_cov.row_sizes = row_sizes

    print("Solving Max Coverage...")
    solver_cov.search_uf_cover()
    print(f"  Coverage: {solver_cov.best_coverage} units  |  Intervals used: {solver_cov.best_density}")

    solver_den = Algorithm()
    solver_den.best_density = -1
    builder_den = SpectrumMatrixBuilder(solver_den.header)
    headers_den, _ = builder_den.build_from_numpy(matrix, Node, ColumnNode)
    solver_den.feasible_count = len(headers_den)
    solver_den.row_sizes = row_sizes

    print("Solving Max Density...")
    solver_den.search_uf_density()
    print(f"  Coverage: {solver_den.best_coverage} units  |  Intervals used: {solver_den.best_density}")

    visualize_intervals(
        matrix, intervals, DOMAIN_LENGTH,
        cov_solution=solver_cov.best_solution,
        den_solution=solver_den.best_solution,
        cov_coverage=solver_cov.best_coverage,
        cov_density=solver_cov.best_density,
        den_coverage=solver_den.best_coverage,
        den_density=solver_den.best_density
    )


if __name__ == "__main__":
    main()