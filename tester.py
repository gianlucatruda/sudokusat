"""Simple testing kit to verify if solver works correctly"""

from tqdm import tqdm
from copy import deepcopy as dcopy
from algorithm import Solver, verify_sat
from data_loader import read_data
from rule_io import read_rules
from loguru import logger
import os

LOGDIR = 'logs/'
LOGLEVEL = 'INFO'

# Configure logging to file
if not os.path.exists(LOGDIR):
    os.makedirs(LOGDIR)
logger.add("logs/file_{time}.log", level=LOGLEVEL)


def test_solver(fname='data/1000 sudokus.txt', n=50):
    """Tests the SAT Solver on `n` sudokus from `fname`
    """

    logger.warning(f"Testing solver on first {n} sudokus in {fname}:\n\n")

    rules = read_rules('sudoku-rules.txt')
    sudokus = read_data('data/1000 sudokus.txt')

    passcount, failcount, timeouts = 0, 0, 0

    for s in tqdm(sudokus[:n]):
        try:
            sigma = dcopy(rules)
            sigma.extend(s)
            orig_sigma = dcopy(sigma)
            solver = Solver(sigma)
            res = solver.solve()
            var = solver.variables
            if solver.timedout:
                timeouts += 1
            elif (verify_sat(orig_sigma, var) == res):
                passcount += 1
            else:
                failcount += 1
            logger.warning(solver)
        except Exception as e:
            logger.error(e)
            failcount += 1
        finally:
            status_update = f'Pass: {passcount} Fail: {failcount} Timeout: {timeouts}'
            logger.warning(status_update)

    logger.warning(status_update)


if __name__ == '__main__':
    print(f'Logging test results to log file...')
    test_solver(n=1000)
