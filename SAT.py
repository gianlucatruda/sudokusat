"""CLI wrapper for the sudokusat application."""

import argparse
import os
import pathlib
from algorithm import Solver, verify_sat
from heuristics import random_split, moms_split, jeroslow_wang_split
from sudoku_verifier import is_valid, build_grid
from io_tools import read_dimacs
from loguru import logger
import sys


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='General purpose SAT solver for sukoku applications.')
    parser.add_argument('input_file', help='The path of a DIMACS file to solve.',
                        type=str)
    parser.add_argument('-S', type=int,
                        required=False, choices=[1, 2, 3], default=1,
                        help='Specify which heuristic strategy to use. \
                            (1) Random, (2) MOMs, (3) 2-sided JW.')
    parser.add_argument('-b', type=int, required=False, default=400,
                        help='Specify after how many backtracks the \
                            solver should timeout. Default 400.')
    parser.add_argument('--sudoku', default=False, action='store_true',
                        help='If the SAT problem is a sudoku, then print the solution in a grid format.')
    parser.add_argument('-l', type=str, required=False, choices=[
                        'DEBUG', 'INFO', 'WARNING'], default='WARNING', help='The log level to use for stdout.')

    # Parse the CL arguments into a Namespace
    args = parser.parse_args()

    # Verify that file exists
    infile = pathlib.Path(args.input_file)
    if not os.path.exists(infile):
        raise FileExistsError(f"Could not locate '{infile}'")

    # Assign the corresponding splitting heuristic
    heuristic = [random_split, moms_split,
                 jeroslow_wang_split][args.S - 1]
    print(f'Using {heuristic.__name__} heuristic')

    # Verify that backtrack threshold is viable
    if not 5 < args.b < 10000:
        raise ValueError(f'Backtrack threshold should be between 5 and 10000')

    # Configure logging to stderr
    logger.remove()
    logger.add(sys.stderr, level=args.l)

    # Read the data files and run solver
    sigma = read_dimacs(infile)
    solver = Solver(sigma,
                    split_heuristic=heuristic,
                    backtrack_thresh=args.b)
    res = solver.solve()
    var = solver.variables

    if solver.timedout:
        print("The solver timed out before completing.")
    else:
        if res:
            if not verify_sat(sigma, var):
                print("CONFLICT!")
            if args.sudoku:
                grid = build_grid(var)
                print(grid)
        else:
            print('Unsatisfiable')
    exit
