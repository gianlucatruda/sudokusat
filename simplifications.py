"""Implementations of DPLL simplification rules"""

def tautology(arr):
    """Detects and removes tautologies"""
    new_arr = []
    for clause in arr:
        new_clause = clause
        for literal in clause:
            neg_lit = -1 * literal
            if neg_lit in clause:
                if literal in new_clause:
                    new_clause.remove(literal)
                elif neg_lit in new_clause:
                    new_clause.remove(neg_lit)
        new_arr.append(new_clause)
    return new_arr
    

def unit_clause(arr):
    """Converts unit clauses to True"""
    new_arr = []
    for clause in arr:
        new_clause = clause
        if len(clause) is 1:
            # TODO try just not appending anything
            new_clause = [True]
        new_arr.append(new_clause)
    return new_arr


def pure_literals(arr):
    """Returns a sorted list of the pure literals in the expression"""
    literals = list(set([y for x in arr for y in x]))
    pos = [x for x in literals if x > 0]
    neg = [-1*x for x in literals if x < 0]
    pures = px for x in pos if x not in neg]
    pures.extend([x for x in neg if x not in pos])
    return sorted(pures)

