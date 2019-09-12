"""Standing IO for sudoku CNF expressions"""

import os


def read_rules(fname: str):
    """Read sudoku rules from a file to list of lists
    """

    if not os.path.exists(fname):
        raise FileNotFoundError

    with open(fname, 'r') as infile:
        rules = infile.readlines()

    # Retrieve all lines that end with '0', split on spaces.
    sudoku_rules = [
        [int(y) for y in x.split(' ')]
        for x in [z[:-3] for z in rules if z[-2] == '0']]

    assert(len(sudoku_rules) > 0)
    return sudoku_rules
