"""Optimisation heuristics for DPLL algorithm"""

from typing import List, Tuple
from random import choice
from collections import Counter
from copy import deepcopy as dcopy
import math


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

    # Step 1 : Find Clause with Minimum Size
    new_sigma = dcopy(sigma)
    new_sigma.sort(key=lambda arr: len(arr))
    min_size_clause = new_sigma[0]

    # Step 2 : Find the literal with maximum occurrence (positive or negative)
    # All literals are set to negative and added to min_size_clause -->
    # detect total occurrence (negative and positive) of literals
    for literal in min_size_clause:
        neg_lit = -1 * literal
        min_size_clause.append(neg_lit)
        # max. total occurrence of a literal gets selected
        lit_max_occurrence = Counter(min_size_clause).sort()
    predicate = next(iter(lit_max_occurrence))

    # TODO re-evaluate this
    # Choose a value (randomly)
    val = choice([True, False])

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

    # Dictionary containing all different literals and their scores
    literals_and_scores = {}

    # iterate over all clauses, identifies literal with max. occurrence in a certain clause
    for clause in sigma:
        new_clause = clause
        for literal in clause:
            # inverse literals so that negatives and positives will be counted as one literal identity
            neg_lit = -1 * literal
            new_clause = new_clause.append(neg_lit)
            # creates sorted list of occurrences of literals
        literal_counter_list = Counter(new_clause).values().sort()
        print(literal_counter_list)

        lit_max_occurrence = literal_counter_list.keys()[0]
        print('literal, that occurs most often:', lit_max_occurrence)

        sum_lit_max_occurrence = literal_counter_list.values()[0]
        print('the literal', lit_max_occurrence,
              'occurs ', sum_lit_max_occurrence, 'times.')

        score_lit_max_occurrence = sum_lit_max_occurrence * \
            math.pow(2, -len(clause))
        literals_and_scores.update(
            {lit_max_occurrence: score_lit_max_occurrence})

    literals_and_scores_sorted = literals_and_scores.values().sort()[0]
    predicate = next(iter(literals_and_scores_sorted))

    # TODO re-evaluate this
    # Choose a value (randomly)
    val = choice([True, False])

    return predicate, val
