"""Implementation of DPLL algorithm"""

import rule_io
import data_loader
from simplifications import tautology, unit_clause, pure_literals
from random import choice
import copy
from copy import deepcopy as dcopy
from loguru import logger
from abc import ABC
from typing import List, Tuple


BACKTRACK_THRESHOLD = 100  # How many backtracks before timeing out


class Solver(ABC):
    """General-purpose Satisfiability solver.
    """

    def __init__(self, sigma: List[List[int]]):
        """Constructor for `Solver` class

        Parameters
        ----------
        sigma : List[List[int]]
            A PL expression in DIMACS encoding.
            The literals are integers (+ for True, - for False).
            The clauses are lists of those integers.
        """

        self.__sigma = dcopy(sigma)
        self.sigma = sigma
        collapsed = list(set([abs(y) for x in sigma for y in x]))
        self.variables = {k: None for k in collapsed}
        self.__splits = 0
        self.__backtracks = 0
        self.__dpll_calls = 0

    def solve(self) -> bool:
        """Find whether the embedded PL expression is `SAT` or `UNSAT`

        Returns
        -------
        bool
            `True` if satisfiable, else `False`.
            (Note: will also be `False` in case of timeout.)
        """
        res, self.variables = self.__dpll(self.sigma, self.variables)
        if res:
            logger.warning('SAT')
        else:
            logger.warning('UNSAT')
        return res

    def __dpll(self, sigma, variables) -> Tuple[bool, dict]:
        """Apply DPLL algorithm to some expression `sigma` and `variables`

        Returns
        -------
        Tuple
            The satisfiability of the expression, the variable values.
        """

        self.__dpll_calls += 1
        if self.__backtracks > BACKTRACK_THRESHOLD:
            logger.error(f'Timeout after {BACKTRACK_THRESHOLD} backtracks!')
            return False, variables

        logger.debug(
            f'DPLL | Clauses: {len(sigma)}\tUndefined: {len([x for x in list(variables.values()) if x is None])}')

        if len(sigma) < 1:
            logger.info('SAT', sigma)
            logger.info([x for x in variables.keys() if variables[x] == True])
            return True, variables
        elif [] in sigma:
            logger.info('UNSAT')
            return False, variables
        # Simplify (tautologies, unit clauses, pure literals)
        else:
            old_sigma = [[]]
            new_sigma = dcopy(sigma)
            new_variables = dcopy(variables)
            new_sigma = tautology(new_sigma)
            new_sigma = self.__assign_simplify(new_sigma, new_variables)
            while self.__diff_shape(old_sigma, new_sigma) and len(new_sigma) > 1 and [] not in new_sigma:
                old_sigma = dcopy(new_sigma)
                new_sigma, new_variables = pure_literals(
                    new_sigma, new_variables)
                new_sigma, new_variables = unit_clause(
                    new_sigma, new_variables)
                new_sigma = self.__assign_simplify(new_sigma, new_variables)

            if len(new_sigma) < 1 or [] in sigma:
                return self.__dpll(new_sigma, new_variables)

            # Split with recursive call if needed
            sigma_pre_split = dcopy(new_sigma)
            # Choose a predicate (randomly) from unassigned variables
            predicate = choice(
                [k for k in variables.keys() if variables[k] is None])
            # Choose a value (randomly)
            val = choice([True, False])
            # Set predicate to value and recurse
            new_variables[predicate] = val
            new_sigma = self.__assign_simplify(new_sigma, variables)
            logger.debug(f"SPLIT: {predicate} = {val}")
            self.__splits += 1
            res, var = self.__dpll(new_sigma, new_variables)
            if not res:
                self.__backtracks += 1
                logger.debug(f"BACKTRACK: {predicate} = {not val}")
                val = not val
                variables[predicate] = val
                new_sigma = self.__assign_simplify(sigma_pre_split, variables)
                return self.__dpll(sigma_pre_split, variables)
            else:
                return res, var

    def __diff_shape(self, a: List[List], b: List[List]) -> bool:
        """Compare shape of two nested lists

        This is useful for determining if simplifications have
        worked effectively.

        Parameters
        ----------
        a : List[List]
            A list of lists
        b : List[List]
            A list of lists

        Returns
        -------
        bool
            `True` if the lists have different shapes, else `False`
        """

        shape_a = (len(a), len([y for x in a for y in x]))
        shape_b = (len(a), len([y for x in b for y in x]))

        if shape_a == shape_b:
            return False
        else:
            return True

    def __assign_simplify(self, sigma: List[List], values: dict) -> List[List]:
        """Fill the values into the expression and simplify

        Parameters
        ----------
        sigma : List[List]
            A PL expression to assign values to and simplify.
        values : dict
            A dictionary lookup of the literal name and the value to
            use during assignment.

        Returns
        -------
        List[List]
            A nested list of `int` or `bool` literals similar to `sigma`
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

    def __repr__(self):
        """String formatting for the class
        """
        return "<algorithm.Solver metrics={}".format({
            'splits': self.__splits,
            'backtracks': self.__backtracks,
            'calls:': self.__dpll_calls
        })


def verify_sat(sigma: List[List], end_values: dict) -> bool:
    """Verifies that found values satisfy expression

    Parameters
    ----------
    sigma : List[List]
        A PL expression to assign values to and simplify.
    end_values : dict
        A dictionary lookup of the literal name and the value to
        use during assignment.

    Returns
    -------
    bool
        `True` if the values satisfy the expression, else `False`
    """
    new_sigma = []
    for clause in sigma:
        new_clause = []
        for lit in clause:
            val = end_values[abs(lit)]
            if val is not None:
                new_clause.append(
                    val) if lit > 0 else new_clause.append(not val)
        new_sigma.append(new_clause)
    assert(len(new_sigma) == len(sigma))
    for i, clause in enumerate(new_sigma):
        if not any(clause):
            logger.error(f'Clause {i} untrue: {sigma[i]} -> {clause}')
            return False
    return True
