"""Implementations of DPLL simplification rules"""

from typing import List, Tuple
from itertools import chain


def tautology(sigma: List[List]) -> List[List]:
    """Detects and removes tautologies

    Parameters
    ----------
    sigma : List[List]
        A PL expression in DIMACS encoding.
        The literals are integers (+ for True, - for False) or booleans,
        as they are gradually replaced by their values.
        The clauses are lists of those integers or booleans.

    Returns
    -------
    List[List]
        A nested list of `int` or `bool` literals similar to `sigma`
    """
    new_sigma = []
    for clause in sigma:
        new_clause = clause
        for literal in clause:
            neg_lit = -1 * literal
            if neg_lit in clause:
                new_clause.remove(literal)
                new_clause.remove(neg_lit)
        if len(clause) > 0:
            new_sigma.append(new_clause)
    return new_sigma


def unit_clause(sigma: List[List], variables: dict) -> Tuple:
    """Assigns unit clauses to `True` and removes them

    Parameters
    ----------
    sigma : List[List]
        A PL expression in DIMACS encoding.
        The literals are integers (+ for True, - for False) or booleans,
        as they are gradually replaced by their values.
        The clauses are lists of those integers or booleans.
    values : dict
        A dictionary lookup of the literal name and the value.

    Returns
    -------
    Tuple
        A nested list of `int` or `bool` literals similar to `sigma`
        and an updated copy of the `variables` dictionary.
    """
    new_variables = variables
    new_sigma = []
    for clause in sigma:
        new_clause = clause
        if len(clause) is not 1:
            new_sigma.append(new_clause)
        else:
            unit = clause[0]
            old_val = new_variables[abs(unit)]
            new_val = False if unit < 0 else True
            if old_val is None:
                new_variables[abs(unit)] = new_val
            if new_val != old_val and old_val is not None:
                new_sigma.append([])
    return new_sigma, new_variables


def pure_literals(sigma: List[List], variables: dict) -> Tuple:
    """Sets pure literals to their corresponding value

    Parameters
    ----------
    sigma : List[List]
        A PL expression in DIMACS encoding.
        The literals are integers (+ for True, - for False) or booleans,
        as they are gradually replaced by their values.
        The clauses are lists of those integers or booleans.
    values : dict
        A dictionary lookup of the literal name and the value.

    Returns
    -------
    Tuple
        A nested list of `int` or `bool` literals similar to `sigma`
        and an updated copy of the `variables` dictionary.
    """
    # literals = list(set([y for x in sigma for y in x]))
    literals = list(set(list(chain.from_iterable(sigma))))
    bools = [True, False]
    pos = [x for x in literals if x > 0 and x not in bools]
    neg = [x for x in literals if x < 0 and x not in bools]
    pures = [x for x in pos if (-1 * x) not in neg]
    pures.extend([x for x in neg if (-1 * x) not in pos])
    # print(f'Pures: {pures}')
    for p in pures:
        old_val = variables[abs(p)]
        new_val = True if p > 0 else False
        if old_val is not None and old_val != new_val:
            sigma = [[]]
        else:
            variables[abs(p)] = new_val

    return sigma, variables
