"""Simple testing kit to verify if solver works correctly"""

from tqdm import tqdm
from copy import deepcopy as dcopy
from sudoku_verifier import is_valid
from algorithm import Solver, verify_sat
from data_loader import read_data
from rule_io import read_rules
from loguru import logger
import pandas as pd
import os

LOGDIR = 'logs/'
LOGLEVEL = 'INFO'

# Configure logging to file
if not os.path.exists(LOGDIR):
    os.makedirs(LOGDIR)
logger.add("logs/file_{time}.log", level=LOGLEVEL)


def test_solver(fname='data/1000 sudokus.txt', n=50, return_dataframe=False):
    """Tests the SAT Solver on `n` sudokus from `fname`
    """

    # Create array to store performance stats
    stats = []

    logger.warning(f"Testing solver on first {n} sudokus in {fname}:\n\n")

    rules = read_rules('sudoku-rules.txt')
    sudokus = read_data('data/1000 sudokus.txt')

    passcount, failcount, timeouts = 0, 0, 0

    for s in tqdm(sudokus[:n]):
        perf = {'puzzle': s, 'correct': False}
        try:
            sigma = dcopy(rules)
            sigma.extend(s)
            orig_sigma = dcopy(sigma)
            solver = Solver(sigma)
            res = solver.solve()
            var = solver.variables
            perf = solver.performance
            perf['puzzle'] = s

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
    if return_dataframe:
        return pd.DataFrame(stats)

if __name__ == '__main__':
    print(f'Logging test results to log file...')
    df = test_solver(n=1000, return_dataframe=True)
    print(df.describe())

    df.to_csv('results.csv')