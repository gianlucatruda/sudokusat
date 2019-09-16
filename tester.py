from tqdm import tqdm
from copy import deepcopy as dcopy
from algorithm import Solver, verify_sat
from data_loader import read_data
from rule_io import read_rules
from loguru import logger
logger.level('WARNING')


def test_solver(fname='data/1000 sudokus.txt', n=50):
    """Tests the SAT Solver on `n` sudokus from `fname`
    """

    logger.warning(f"Testing solver on first {n} sudokus in {fname}:\n\n")

    rules = read_rules('sudoku-rules.txt')
    sudokus = read_data('data/1000 sudokus.txt')

    passcount, failcount = 0, 0

    for s in tqdm(sudokus[:n]):
        sigma = dcopy(rules)
        sigma.extend(s)
        orig_sigma = dcopy(sigma)
        solver = Solver(sigma)
        res = solver.solve()
        var = solver.variables
        if (verify_sat(orig_sigma, var) == res):
            passcount += 1
        else:
            failcount += 1
        print(solver)
        print(f'Pass: {passcount}\tFail: {failcount}')
