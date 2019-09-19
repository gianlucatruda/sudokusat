"""Verifies that it's a valid sudoku and depicts"""

import numpy as np


def is_valid(variables, sudoku_sigma, shape=(9, 9)):
    """Verifies that variable state is a valid solution to given sudoku
    """

    if shape[0] != shape[1]:
        raise ValueError('Only square sudokus supported')

    # Get all the true variables
    truths = [x for x in variables if variables[x] is True]
    # Get the starting true variables
    game_start = list(set([y for x in sudoku_sigma for y in x]))
    # Verify that solution upholds game start rules
    for x in game_start:
        if x not in truths:
            print(f'Missing start condition: {x}')
            return False

    if shape[0]**2 != len(truths):
        print(f'Solutions of wrong shape: {len(truths)}')
        return False

    block_side = int(np.sqrt(shape[0]))
    # Build the grid in standard sudoku style
    grid = np.array([x % 10 for x in sorted(truths)]).reshape(shape)
    # Now verify that it's a valid sudoku
    for direction in [
        grid,  # Groups are rows
        grid.T,  # Groups are columns
        [(grid[a:a+block_side, b:b+block_side]).reshape(shape[0])
            for a in range(0, shape[0], block_side)
            for b in range(0, shape[0], block_side)]  # Groups are blocks
    ]:
        for group in direction:  # Checks every row, col, and block
            if sum(group) != sum(range(1, shape[0]+1)):
                print(f'summation of group: {group}')
                return False

    return True


def build_grid(variables, shape=(9,9)):
    """Builds a visual representation of the sudoku solution"""

    truths = [x for x in variables if variables[x] is True]
    grid = np.array([x % 10 for x in sorted(truths)]).reshape(shape)

    return grid
