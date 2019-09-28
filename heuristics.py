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

    # Get a list of all literals in sigma
    lits = list(chain.from_iterable(sigma))
    # Choose a predicate (randomly) from literals
    predicate = abs(choice(lits))
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

    # Step 1 : Find Clauses with Minimum Size
    minsize = np.min([len(c) for c in sigma])
    min_clauses = [x for x in sigma if len(x) == minsize]
    min_lits = list(set(list(chain.from_iterable(min_clauses))))

    def __mom_func(lit, k=2):
        _lit = abs(lit)
        count_lit = min_lits.count(_lit)
        count_not_lit = min_lits.count(-1*_lit)
        return (count_lit + count_not_lit) * 2**k + \
            (count_lit * count_not_lit)

    # Step 2 : Find the literal with maximum occurrence (positive or negative)
    mom_scores = list(map(__mom_func, min_lits))
    predicate = abs(min_lits[mom_scores.index(max(mom_scores))])

    # Step 3: When the highest ranked variable is found, it is instantiated
    # to true if the variable appears in more smallest clauses as a
    # positive literal and to false otherwise.

    def __pos_neg_occurences(lit, literals):
        _lit = abs(lit)
        return literals.count(lit), literals.count(-1*lit)

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

    predicate = abs(max(two_side_scores, key=two_side_scores.get))
    # From the theory, this should be the other way around, I think
    # But for some reason THIS was round is much much faster
    val = False if scores[predicate] >= scores[-1 * predicate] else True

    return predicate, val
