"""Implementations of DPLL simplification rules"""

import copy

def tautology(sigma):
    """Detects and removes tautologies"""
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


def unit_clause(sigma, variables):
    """Assigns unit clauses to True and removes"""
    new_variables = copy.deepcopy(variables)
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
                print("Hold up!")
                new_sigma.append([])
    return new_sigma, new_variables


def pure_literals(sigma, variables):
    """Sets pure literals to corresponding value
    """
    new_sigma = copy.deepcopy(sigma)
    new_variables = copy.deepcopy(variables)
    literals = list(set([y for x in sigma for y in x]))
    bools = [True, False]
    pos = [x for x in literals if x > 0 and x not in bools]
    neg = [x for x in literals if x < 0 and x not in bools]
    pures = [x for x in pos if (-1 * x) not in neg]
    pures.extend([x for x in neg if (-1 * x) not in pos])
    print(f'Pures: {pures}')
    for p in pures:
        old_val = new_variables[abs(p)]
        new_val = True if p > 0 else False
        if old_val is not None and old_val != new_val:
            new_sigma = [[]]
        else:
            new_variables[abs(p)] = new_val

    return new_sigma, new_variables
