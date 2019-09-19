"""Optimisation heuristics for DPLL algorithm"""

from typing import List, Tuple
from random import choice


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


# TODO implement
def splitting_heuristic_01(sigma: List[List], variables: dict) -> Tuple:
    """[Description]

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

    predicate, val = 0, 0

    return predicate, val

# TODO implement


def splitting_heuristic_02(sigma: List[List], variables: dict) -> Tuple:
    """[Description]

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

    predicate, val = 0, 0

    return predicate, val
