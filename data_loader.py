"""Reads sudoku data files"""

import os


def read_data(fname: str, shape=(9, 9)):
    """Read a sudoku data file and convert to DIMACS.
    """

    if not os.path.exists(fname):
        raise FileNotFoundError

    with open(fname, 'r') as infile:
        sudoku_data = infile.readlines()

    sudokus = []

    for line in sudoku_data:
        dimacs = []
        for x in range(1, shape[0] + 1):
            for y in range(1, shape[1] + 1):
                char = line[(9 * x) + y - 10]
                if char != '.':
                    dimacs.append([int(f'{x}{y}{char}')])
        sudokus.append(dimacs)

    return sudokus
