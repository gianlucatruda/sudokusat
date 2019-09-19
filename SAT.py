"""CLI wrapper for the sudokusat application."""

import argparse
import os
import pathlib
from algorithm import Solver
from sudoku_verifier import is_valid, build_grid
from rule_io import read_rules


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='General purpose SAT solver for sukoku applications.')
    parser.add_argument('input_file', type=str, nargs=1)
    parser.add_argument('-S', type=int, nargs=1,
                        required=False, choices=[1, 2, 3], default=1,
                        help='Specify which heuristic strategy to use.')

    args = parser.parse_args()
    infile = pathlib.Path(args.input_file[0])
    if not os.path.exists(infile):
        raise FileExistsError(f"Could not locate '{infile}'")


    sigma = read_rules(infile)
    solver = Solver(sigma)
    res = solver.solve()
    var = solver.variables

    if solver.timedout:
        print("The solver timed out before completing.")
    else:
        if res:
            grid = build_grid(var)
            print(grid)
        else:
            print('Unsatisfiable')

    exit
