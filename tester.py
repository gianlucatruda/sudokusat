"""Simple testing kit to verify if solver works correctly"""

from tqdm import tqdm
from copy import deepcopy as dcopy
from sudoku_verifier import is_valid
from algorithm import Solver, verify_sat
from heuristics import random_split, moms_split, jeroslow_wang_split
from io_tools import read_sudokus, read_dimacs
from loguru import logger
import pandas as pd
import os
from datetime import datetime
import sys
import ast
import time
from pathlib import Path
import argparse


LOGDIR = 'logs/'
CACHE = 'checkpoints/'


def test_solver(dataset: pd.DataFrame, split_heuristic, sample=None, cache=None, **kwargs):
    """Tests the SAT Solver on sudokus in a DataFrame
    """

    if not isinstance(dataset, pd.DataFrame):
        raise ValueError('Requires a dataframe as input.')

    if cache is not None:
        cache = Path(cache)
        if not os.path.exists(cache):
            os.makedirs(cache)

    if sample is None:
        df = dataset.copy()
    else:
        df = dataset.copy().sample(sample)

    # Create array to store performance stats
    stats = []

    rules = read_dimacs('sudoku-rules.txt')
    sudokus = [ast.literal_eval(puzzle) for puzzle in df.puzzle.values]

    passcount, failcount, timeouts = 0, 0, 0
    logger.warning(f"Testing solver on {len(sudokus)} sudokus\n\n")

    for i, s in enumerate(tqdm(sudokus)):
        perf = {'puzzle': s, 'correct': False}
        try:
            sigma = dcopy(rules)
            sigma.extend(s)
            orig_sigma = dcopy(sigma)
            solver = Solver(sigma, split_heuristic=split_heuristic, **kwargs)
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

        if i % 300 == 0 and i > 0 and cache is not None:
            try:
                # Persist the results (so far) to disk
                now = datetime.now().strftime('%m-%d-%H_%M_%S')
                cache_name = f"{cache}/{now}_{split_heuristic.__name__}.csv"
                pd.DataFrame(stats).to_csv(cache_name)
                logger.warning(f'Latest cache: {cache_name}')
            except Exception as e:
                logger.warning(e)

    logger.warning(status_update)

    return pd.DataFrame(stats)


def test_solver_general(dataset: pd.DataFrame, split_heuristic, sample=None, cache=None, **kwargs):
    """Tests the SAT Solver on general CNF files listed in a DataFrame
    """

    if not isinstance(dataset, pd.DataFrame):
        raise ValueError('Requires a dataframe as input.')

    if cache is not None:
        cache = Path(cache)
        if not os.path.exists(cache):
            os.makedirs(cache)

    if sample is None:
        df = dataset.copy()
    else:
        df = dataset.copy().sample(sample)

    # Create array to store performance stats
    stats = []

    rules = read_dimacs('sudoku-rules.txt')
    problems = [file for file in df['file'].values]

    passcount, failcount, timeouts = 0, 0, 0
    logger.warning(f"Testing solver on {len(problems)} problems\n\n")

    for i, file in enumerate(tqdm(problems)):
        try:
            s = read_dimacs(file)
        except Exception as e:
            logger.warning(f'Could not find {file} because: {e}')
            continue

        perf = {'problem': file, 'correct': False}
        try:
            sigma = dcopy(rules)
            sigma.extend(s)
            orig_sigma = dcopy(sigma)
            solver = Solver(sigma, split_heuristic=split_heuristic, **kwargs)
            start_time = time.time()
            res = solver.solve()
            solve_time = time.time() - start_time
            var = solver.variables
            perf = solver.performance
            perf['problem'] = file
            perf['running_time'] = solve_time

            if solver.timedout:
                timeouts += 1
                perf['correct'] = False

            # If the SAT solution is viable
            elif (verify_sat(orig_sigma, var) == res):
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

        if i % 300 == 0 and i > 0 and cache is not None:
            try:
                # Persist the results (so far) to disk
                now = datetime.now().strftime('%m-%d-%H_%M_%S')
                cache_name = f"{cache}/{now}_{split_heuristic.__name__}.csv"
                pd.DataFrame(stats).to_csv(cache_name)
                logger.warning(f'Latest cache: {cache_name}')
            except Exception as e:
                logger.warning(e)

    logger.warning(status_update)

    return pd.DataFrame(stats)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Testing system for SAT solver applied to sudoku.')
    parser.add_argument('dataset', type=str)
    parser.add_argument('-S', type=int,
                        required=False, choices=[1, 2, 3], default=1,
                        help='Specify which heuristic strategy to use. \
                            (1) Random, (2) MOMs, (3) 2-sided JW.')
    parser.add_argument('-n', type=int, required=False,
                        help='The size of the sample to take from the dataset. Default NONE (use all).')

    parser.add_argument('-l', type=str, required=False, choices=[
                        'DEBUG', 'INFO', 'WARNING'], default='WARNING', help='The log level to use for stdout.')

    parser.add_argument('--general', action='store_true', required=False,
                        help='Test on general CNF SAT problems instead of sudokus.')
    parser.add_argument('-b', type=int, required=False, default=400,
                        help='Specify after how many backtracks the \
                            solver should timeout. Default 400.')

    args = parser.parse_args()

    # Configure logging to stderr
    logger.remove()
    logger.add(sys.stderr, level=args.l)

    # Configure logging to file
    if not os.path.exists(LOGDIR):
        os.makedirs(LOGDIR)
    logger.add("logs/{time}.log", level="DEBUG")

    # Assign the corresponding splitting heuristic
    heuristic = [random_split, moms_split,
                 jeroslow_wang_split][args.S - 1]
    print(f'Using {heuristic.__name__} heuristic')

    fname = args.dataset
    dataset = pd.read_csv(fname)

    # Run the tests
    if args.general:
        df = test_solver_general(
            dataset, heuristic, sample=args.n, cache=CACHE, backtrack_thresh=args.b)
    else:
        df = test_solver(dataset, heuristic, sample=args.n,
                         cache=CACHE, backtrack_thresh=args.b)
    print(df.describe())

    # Save results to custom csv file
    now = datetime.now().strftime("%m-%d-%H_%M_%S")
    path = f'results/{fname}'
    if not os.path.exists(path):
        os.makedirs(path)
    outname = f'{path}/{now}_results.csv'
    df.to_csv(outname)
    print(f'Results saved to {outname}')
