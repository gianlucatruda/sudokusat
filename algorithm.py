"""Implementation of DPLL algorithm"""

from simplifications import tautology, unit_clause, pure_literals
from heuristics import random_split
from copy import deepcopy as dcopy
from loguru import logger
from abc import ABC
from typing import List, Tuple


class Solver(ABC):
    """General-purpose Satisfiability solver.
    """

    def __init__(self,
                 sigma: List[List[int]],
                 split_heuristic=random_split,
                 backtrack_thresh=400):
        """Constructor for `Solver` class


        Parameters
        ----------
        sigma : List[List[int]]
            A PL expression in DIMACS encoding.
            The literals are integers (+ for True, - for False).
            The clauses are lists of those integers.
        split_heuristic : function, optional
            The heuristic function to use at the splitting step of
            DPLL algorithm, by default random_split
        backtrack_thresh : int, optional
            The number of backtracks after which the solver should timeout,
            by default 400
        """

        self.__sigma = dcopy(sigma)
        self.sigma = sigma
        self.split_heuristic = split_heuristic
        self.backtrack_threshold = backtrack_thresh
        collapsed = list(set([abs(y) for x in sigma for y in x]))
        self.variables = {k: None for k in collapsed}
        self.__simplifications = 0
        self.__splits = 0
        self.__backtracks = 0
        self.__dpll_calls = 0
        self.__timedout = False
        self.__conclusion = None

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
            self.__conclusion = 'SAT'
        else:
            logger.warning('UNSAT')
            self.__conclusion = 'UNSAT'
        return res

    @property
    def performance(self) -> dict:
        """Returns performance statistics"""
        return {
            'heuristic': self.split_heuristic.__name__,
            'simplifications': self.__simplifications,
            'calls': self.__dpll_calls,
            'splits': self.__splits,
            'backtracks': self.__backtracks,
            'conclusion': 'TIMEOUT' if self.__timedout else self.__conclusion,
        }

    @property
    def timedout(self) -> bool:
        """Whether the solver timed out before reaching a conclusion.

        Returns
        -------
        bool
            `True` if a timeout was logged, else `False`
        """
        return self.__timedout

    @property
    def unknowns(self) -> int:
        """Returns a count of the variables with unknown values.

        Returns
        -------
        int
            The number of undetermined variables (not True or False).
        """

        return len([v for v in self.variables.keys() if self.variables[v] is None])

    def __dpll(self, sigma, variables) -> Tuple[bool, dict]:
        """Apply DPLL algorithm to some expression `sigma` and `variables`

        Returns
        -------
        Tuple
            The satisfiability of the expression, the variable values.
        """
        self.__dpll_calls += 1
        if self.__backtracks > self.backtrack_threshold:
            if not self.__timedout:
                logger.error(
                    f'Timeout after {self.backtrack_threshold} backtracks!')
                self.__timedout = True
            return False, variables

        logger.debug(
            f'DPLL(Clauses: {len(sigma)},\tUndefined: {self.unknowns})')

        # Return SAT if the expression is empty
        if len(sigma) < 1:
            logger.info('SAT', sigma)
            logger.info([x for x in variables.keys() if variables[x] == True])
            return True, variables
        # Return UNSAT if the expression contains empty clause
        elif [] in sigma:
            logger.info('UNSAT')
            return False, variables
        # Simplify (tautologies, unit clauses, pure literals)
        else:
            old_sigma = [[]]
            new_sigma = sigma
            new_variables = variables
            new_sigma = tautology(new_sigma)
            new_sigma = self.__assign_simplify(new_sigma, new_variables)

            # Keep simplifying as long as you can
            while self.__diff_shape(old_sigma, new_sigma) and (
                    len(new_sigma) > 1) and (
                    [] not in new_sigma):

                self.__simplifications += 1
                old_sigma = new_sigma
                new_sigma, new_variables = pure_literals(
                    new_sigma, new_variables)
                new_sigma, new_variables = unit_clause(
                    new_sigma, new_variables)
                new_sigma = self.__assign_simplify(new_sigma, new_variables)

            self.variables = new_variables

            # Check if we now fulfill the criteria for SAT or UNSAT
            if len(new_sigma) < 1 or [] in new_sigma or self.unknowns < 1:
                return self.__dpll(new_sigma, new_variables)

            """SPLITTING------------------------------------------------
            """

            # Copy variables and expression to return to when backtracking
            sigma_pre_split = dcopy(new_sigma)
            variables_pre_split = dcopy(new_variables)

            # Choose predicate and value using a split heuristic function
            # This function is defined separately and fed to the __init__ function.
            predicate, val = self.split_heuristic(new_sigma, new_variables)

            # Set predicate to value and recurse
            new_variables[predicate] = val
            new_sigma = self.__assign_simplify(new_sigma, new_variables)
            logger.debug(f"SPLIT: {predicate} = {val}")
            self.__splits += 1
            res, var = self.__dpll(new_sigma, new_variables)
            if not res:
                self.__backtracks += 1
                logger.debug(f"BACKTRACK: {predicate} = {not val}")

                # Invert the value
                val = not val
                # Go back to the old variables and expression
                variables = variables_pre_split
                sigma = sigma_pre_split
                variables[predicate] = val
                # Simplify and recurse
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

        def no_truths(clause):
            """Checks if not truths in a clause (ignoring literal 1)"""
            for lit in clause:
                if lit is True and isinstance(lit, bool):
                    return False
            return True

        new_sigma = []
        for clause in sigma:
            new_clause = []
            for lit in clause:
                if values[abs(lit)] is not None:
                    val = values[abs(lit)]
                    sign = 1 if lit > 0 else -1
                    lit_val = val if sign == 1 else (not val)
                    if lit_val:
                        new_clause.append(lit_val)
                else:
                    new_clause.append(lit)
            if no_truths(new_clause):  # Keep only if clause contains no `True`
                new_sigma.append(new_clause)

        return new_sigma

    def __repr__(self):
        """String formatting for the class
        """
        return "<algorithm.Solver metrics={}".format({
            'heuristic': self.split_heuristic.__name__,
            'simplifications': self.__simplifications,
            'splits': self.__splits,
            'backtracks': self.__backtracks,
            'calls:': self.__dpll_calls,
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
                if lit > 0:
                    new_clause.append(val)
                else:
                    new_clause.append(not val)
        new_sigma.append(new_clause)
    assert(len(new_sigma) == len(sigma))
    for i, clause in enumerate(new_sigma):
        if not any(clause):
            logger.error(f'Clause {i} untrue: {sigma[i]} -> {clause}')
            return False
    return True
