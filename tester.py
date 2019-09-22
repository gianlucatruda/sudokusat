"""Simple testing kit to verify if solver works correctly"""

from tqdm import tqdm
from copy import deepcopy as dcopy
from sudoku_verifier import is_valid
from algorithm import Solver, verify_sat
from heuristics import random_split, moms_split, jeroslow_wang_split
from data_loader import read_data
from rule_io import read_rules
from loguru import logger
import pandas as pd
import os
from datetime import datetime
import sys
import ast
import time


def test_solver(dataset: pd.DataFrame, split_heuristic, sample=None):
    """Tests the SAT Solver on sudokus in a DataFrame
    """

    if not isinstance(dataset, pd.DataFrame):
        raise ValueError('Requires a dataframe as input.')

    if sample is None:
        df = dataset.copy()
    else:
        df = dataset.copy().sample(sample)

    # Create array to store performance stats
    stats = []

    rules = read_rules('sudoku-rules.txt')
    sudokus = [ast.literal_eval(puzzle) for puzzle in df.puzzle.values]

    passcount, failcount, timeouts = 0, 0, 0
    logger.warning(f"Testing solver on {len(sudokus)} sudokus\n\n")

    for s in tqdm(sudokus):
        perf = {'puzzle': s, 'correct': False}
        try:
            sigma = dcopy(rules)
            sigma.extend(s)
            orig_sigma = dcopy(sigma)
            solver = Solver(sigma, split_heuristic=split_heuristic)
            start_time = time.time()
            res = solver.solve()
            solve_time = time.time() - start_time
            var = solver.variables
            perf = solver.performance
            perf['puzzle'] = s
            perf['running_time'] = solve_time

            if solver.timedout:
                timeouts += 1
                perf['correct'] = False

            # If the SAT solution is viable AND it's a correct sudoku
            elif (verify_sat(orig_sigma, var) == res) and is_valid(var, s):
                passcount += 1
                perf['correct'] = True
            else:
                failcount += 1
                perf['correct'] = False
            logger.warning(solver)
        except Exception as e:
            logger.error(e)
            failcount += 1
        finally:
            stats.append(perf)
            status_update = f'Pass: {passcount} Fail: {failcount} Timeout: {timeouts}'
            logger.warning(status_update)
    logger.warning(status_update)

    return pd.DataFrame(stats)


if __name__ == '__main__':

    LOGDIR = 'logs/'
    LOGLEVEL = 'INFO'
    HEURISTIC = random_split
    SAMPLE = None

    # Configure logging to stderr
    logger.remove()
    logger.add(sys.stderr, level="WARNING")

    # Configure logging to file
    if not os.path.exists(LOGDIR):
        os.makedirs(LOGDIR)
    logger.add("logs/file_{time}.log", level=LOGLEVEL)

    args = sys.argv
    if len(args) != 2:
        print('Pass in the filename as an argument!')
        sys.exit(1)
    fname = args[1]
    dataset = pd.read_csv(fname)
    df = test_solver(dataset, HEURISTIC, sample=SAMPLE)
    print(df.describe())

    # Save results to custom csv file
    now = datetime.now().strftime("%m-%d-%H_%M_%S")
    path = f'results/{fname}'
    if not os.path.exists(path):
        os.makedirs(path)
    outname = f'{path}/{now}_results.csv'
    df.to_csv(outname)
    print(f'Results saved to {outname}')
