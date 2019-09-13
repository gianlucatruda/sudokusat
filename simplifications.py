"""Implementations of DPLL simplification rules"""


def tautology(sigma):
    """Detects and removes tautologies"""
    new_sigma = []
    for clause in sigma:
        new_clause = clause
        for literal in clause:
            neg_lit = -1 * literal
            if neg_lit in clause:
                if literal in new_clause:
                    new_clause.remove(literal)
                elif neg_lit in new_clause:
                    new_clause.remove(neg_lit)
        new_sigma.append(new_clause)
    return new_sigma


def unit_clause(sigma, variables):
    """Assigns unit clauses to True and removes"""
    new_sigma = []
    for clause in sigma:
        new_clause = clause
        if len(clause) is not 1:
            new_sigma.append(new_clause)
        else:
            unit = clause[0]
            if unit < 0:
                variables[unit] = False  # TODO should we mutate `variables`?
            else:
                variables[unit] = True
    return new_sigma, variables


def pure_literals(sigma, variables):
    """Sets pure literals to corresponding value
    """
    literals = list(set([y for x in sigma for y in x]))

    pos = [x for x in literals if x > 0]
    neg = [x for x in literals if x < 0]
    pures = [x for x in pos if (-1 * x) not in neg]
    pures.extend([x for x in neg if (-1 * x) not in pos])

    # TODO ensure this concurs with theory
    for p in pures:
        if p > 0:
            variables[p] = True
        else:
            variables[p] = False

    return sigma, variables
