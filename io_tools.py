"""Standing IO for sudoku CNF expressions"""

import os
from typing import List
from pathlib import Path


def read_dimacs(fname: str, sep=' ') -> List[List]:
    """Read DIMACS from a file to list of lists

    Parameters
    ----------
    fname : str
        Full path of a DIMACS file representing CNF logic.
    sep : str, optional
        The separator used between CNF literals, by default ' '

    Returns
    -------
    List[List]
        Sigma—a list of clauses (each of which is a list of
        integer literals).
    """

    ignore_line_chars = ['p', 'c']

    if not os.path.exists(fname):
        raise FileNotFoundError

    with open(fname, 'r') as infile:
        rules = infile.readlines()

    # Retrieve all data lines that end with '0', split on separator.
    clauses = []
    for line in rules:
        l = line.strip()
        if len(l) > 1:
            if l[0] not in ignore_line_chars:
                clauses.append([int(x) for x in l[:-2].split(sep)])

    return clauses


def write_dimacs(fname: str, values: dict):
    """Writes assigned values to file in DIMACS style.

    Parameters
    ----------
    fname : str
        Path to output file.
    values : dict
        The assigned variable:value lookup dict.
    """

    fpath = Path(fname).parents[0]
    print(fpath)
    if not os.path.exists(fpath):
        os.makedirs(fpath)

    output = ''

    for variable, value in values.items():
        if value is None or value is False:
            output += f'-{variable} '
        else:
            output += f'{variable} '

    with open(fname, 'w') as outfile:
        outfile.write(output)


def read_sudokus(fname: str, shape=(9, 9)) -> List[List[List]]:
    """Read a sudoku data file, convert to DIMACS, and generate sigmas.

    Parameters
    ----------
    fname : str
        The path of the sudoku data file.
    shape : tuple, optional
        Shape of the sudokus in the file, by default (9, 9).
        Max: 9x9 supported.

    Returns
    -------
    List[List[List]]
        The CNF version of the sudoku data file encoded as a 3D list.
        Each outermost list item is a `sigma` for one puzzle, encoded
        as a list of clauses.
    """

    if not os.path.exists(fname):
        raise FileNotFoundError(f'{fname}')

    if shape[0] > 9 or shape[1] > 9:
        raise ValueError('9x9 is max sudoku size supported.')

    with open(fname, 'r') as infile:
        sudoku_data = infile.readlines()

    sudokus = []

    for line in sudoku_data:
        dimacs = []
        for x in range(1, shape[0] + 1):
            for y in range(1, shape[1] + 1):
                char = line[(shape[0] * x) + y - (shape[0]+1)]
                if char != '.':
                    dimacs.append([int(f'{x}{y}{char}')])
        sudokus.append(dimacs)

    return sudokus
