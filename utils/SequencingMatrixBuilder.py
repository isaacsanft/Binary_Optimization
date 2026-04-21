import numpy as np


def build_sequencing_matrix(n_reads=70, genome_length=250, min_len=15, max_len=60, seed=42):
    rng = np.random.default_rng(seed)
    matrix = np.zeros((n_reads, genome_length), dtype=np.uint8)
    read_intervals = []

    for i in range(n_reads):
        length = int(rng.integers(min_len, max_len + 1))
        start = int(rng.integers(0, genome_length - length + 1))
        end = start + length
        matrix[i, start:end] = 1
        read_intervals.append((start, end))

    return matrix, read_intervals