"""Implementation of DPLL algorithm"""

import rule_io
import data_loader
from simplifications import tautology, unit_clause, pure_literals
from random import choice
import copy
from copy import deepcopy as dcopy
from loguru import logger
from abc import ABC
from typing import List


BACKTRACK_THRESHOLD = 200


class Solver(ABC):

    def __init__(self, sigma: List):
        self.__sigma = dcopy(sigma)
        self.sigma = sigma
        collapsed = list(set([abs(y) for x in sigma for y in x]))
        self.variables = {k: None for k in collapsed}
        self.__splits = 0
        self.__backtracks = 0
        self.__dpll_calls = 0

    def solve(self):
        res, var = self.dpll(self.sigma, self.variables)
        return res

    def dpll(self, sigma, variables):
        """Apply DPLL algorithm to some expression `sigma`

        sigma must be a list of lists of integers representing
        DIMACS notation for the problem.

        """

        self.__dpll_calls += 1
        if self.__backtracks > BACKTRACK_THRESHOLD:
            logger.error(f'Timeout after {BACKTRACK_THRESHOLD} backtracks!')
            return False, variables

        logger.debug(
            f'DPLL: {len(sigma)} {len([x for x in list(variables.values()) if x is None])}')

        if len(sigma) < 1:
            logger.warning('SAT', sigma)
            logger.debug([x for x in variables.keys() if variables[x] == True])
            return True, variables
        elif [] in sigma:
            logger.warning('UNSAT')
            return False, variables
        # Simplify (tautologies, unit clauses, pure literals)
        else:
            old_sigma = [[]]
            new_sigma = dcopy(sigma)
            new_variables = dcopy(variables)
            new_sigma = tautology(new_sigma)
            new_sigma = self.assign_simplify(new_sigma, new_variables)
            while self.diff_shape(old_sigma, new_sigma) and len(new_sigma) > 1 and [] not in new_sigma:
                old_sigma = dcopy(new_sigma)
                logger.debug("SIMPLIFY...")
                new_sigma, new_variables = pure_literals(
                    new_sigma, new_variables)
                new_sigma, new_variables = unit_clause(
                    new_sigma, new_variables)
                new_sigma = self.assign_simplify(new_sigma, new_variables)

            if len(new_sigma) < 1 or [] in sigma:
                return self.dpll(new_sigma, new_variables)

            # Split with recursive call if needed
            sigma_pre_split = dcopy(new_sigma)
            # Choose a predicate (randomly) from unassigned variables
            predicate = choice(
                [k for k in variables.keys() if variables[k] is None])
            # Choose a value (randomly)
            val = choice([True, False])
            # Set predicate to value and recurse
            new_variables[predicate] = val
            new_sigma = self.assign_simplify(new_sigma, variables)
            logger.info(f"SPLIT: {predicate} = {val}")
            self.__splits += 1
            res, var = self.dpll(new_sigma, new_variables)
            if not res:
                self.__backtracks += 1
                logger.info(f"BACKTRACK: {predicate} = {not val}")
                val = not val
                variables[predicate] = val
                new_sigma = self.assign_simplify(sigma_pre_split, variables)
                return self.dpll(sigma_pre_split, variables)
            else:
                return res, var

    def diff_shape(self, a, b):
        """Compare shape of two nested lists"""

        shape_a = (len(a), len([y for x in a for y in x]))
        shape_b = (len(a), len([y for x in b for y in x]))

        if shape_a == shape_b:
            return False
        else:
            return True

    def assign_simplify(self, sigma, values):
        """Assigns values to an expression and simplifies
        """

        new_sigma = []

        for clause in sigma:
            new_clause = []
            for lit in clause:
                if lit in [True, False]:
                    if lit:
                        new_clause.append(lit)
                elif values[abs(lit)] is not None:
                    val = values[abs(lit)]
                    sign = 1 if lit > 0 else -1
                    lit_val = val if sign == 1 else (not val)
                    if lit_val:
                        new_clause.append(lit_val)
                else:
                    new_clause.append(lit)
            if new_clause.count(True) is 0:  # Keep only if clause contains no `True`
                new_sigma.append(new_clause)
        return new_sigma


def verify_sat(sigma, end_values):
    """Verifies that found values satisfy expression
    """
    new_sigma = []
    for clause in sigma:
        new_clause = []
        for lit in clause:
            val = end_values[abs(lit)]
            if val is not None:
                new_clause.append(val)

    for i, clause in enumerate(new_sigma):
        if not any(clause):
            logger.warning(f'Clause {i} untrue: {sigma[i]} -> {clause}')
            return False
    return True
