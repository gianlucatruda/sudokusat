"""Optimisation heuristics for DPLL algorithm"""

from typing import List, Tuple
from random import choice
from copy import deepcopy as dcopy
import numpy as np
from itertools import chain
from collections import defaultdict


def random_split(sigma: List[List], variables: dict) -> Tuple:
    """Implements a random splitting heuristic for DPLL.

    Parameters
    ----------
    sigma : List[List]
        A PL expression in DIMACS format.
    variables : dict
        The literal names and current values as a dictionary.

    Returns
    -------
    Tuple
        The selected `predicate` and the selected `value`
    """
    # Choose a predicate (randomly) from unassigned variables
    predicate = choice(
        [k for k in variables.keys() if variables[k] is None])
    # Choose a value (randomly)
    val = choice([True, False])

    return predicate, val


def moms_split(sigma: List[List], variables: dict) -> Tuple:
    """ MOMS (Maximum Occurrence in clauses of Minimum Size) heuristic

    Returns the literal with the most occurrences in all clauses
    of minimum size.

    Parameters
    ----------
    sigma : List[List]
        A PL expression in DIMACS format.
    variables : dict
        The literal names and current values as a dictionary.

    Returns
    -------
    Tuple
        The selected `predicate` and the selected `value`
    """

    def __mom_func(lit, clause, k=2):
        _lit = abs(lit)
        count_lit = clause.count(_lit)
        count_not_lit = clause.count(-1*_lit)
        return (count_lit + count_not_lit) * 2**k + \
            (count_lit * count_not_lit)

    def __pos_neg_occurences(lit, literals):
        _lit = abs(lit)
        return literals.count(lit), literals.count(-1*lit)

    # Step 1 : Find Clauses with Minimum Size
    new_sigma = dcopy(sigma)
    new_sigma.sort(key=lambda arr: len(arr))
    minsize = len(new_sigma[0])
    min_clauses = [x for x in new_sigma if len(x) == minsize]
    min_lits = [y for x in min_clauses for y in x]

    # Step 2 : Find the literal with maximum occurrence (positive or negative)
    momified = {lit: __mom_func(lit, min_lits) for lit in min_lits}
    predicate = abs(max(momified, key=momified.get))

    # Step 3: When the highest ranked variable is found, it is instantiated
    # to true if the variable appears in more smallest clauses as a
    # positive literal and to false otherwise.
    pos_count, neg_count = __pos_neg_occurences(predicate, min_lits)
    val = True if pos_count > neg_count else False

    return predicate, val


def jeroslow_wang_split(sigma: List[List], variables: dict) -> Tuple:
    """ Two Sided Jeroslow-Wang heuristic

    For each literal compute J(l) = \sum{l in clause c} 2^{-|c|}
    Return the literal maximizing J
    Compute J(l) also counts the negation of l = J(x) + J(-x)
    We need to keep track of them separately
    as we return x if J(x) >= J(-x) otherwise -x

    Parameters
    ----------
    sigma : List[List]
        A PL expression in DIMACS format.
    variables : dict
        The literal names and current values as a dictionary.

    Returns
    -------
    Tuple
        The selected `predicate` and the selected `value`
    """

    lits = list(chain.from_iterable(sigma))
    scores = defaultdict(int)

    for clause in sigma:
        weight = 2**(-len(clause))
        for lit in list(set(clause)):
            scores[lit] += weight

    two_side_scores = defaultdict(int)
    for lit in lits:
        two_side_scores[abs(lit)] = scores[lit] + scores[-1*lit]

    predicate = max(two_side_scores, key=two_side_scores.get)
    val = True if scores[predicate] >= scores[-1 * predicate] else False

    return predicate, val
