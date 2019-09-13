"""Implementation of DPLL algorithm"""

from simplifications import tautology, unit_clause, pure_literals
from random import choice


def dpll(sigma, variables):
    """Apply DPLL algorithm to some expression `sigma`

    sigma must be a list of lists of integers representing
    DIMACS notation for the problem.

    """
    print(
        f'DPLL: {len(sigma)} {len([x for x in list(variables.values()) if x is None])}')
    # if expression is empty, then SAT
    if len(sigma) < 1:
        print('SAT')
        print([x for x in variables.keys() if variables[x] is True])
        return True
    # if expression contains empty clause, UNSAT
    elif sigma == [[]]:
        print('UNSAT')
        return False
    # Simplify (tautologies, unit clauses, pure literals)
    else:
        new_sigma = tautology(sigma)
        new_sigma = assign_simplify(new_sigma, variables)
        new_sigma, new_variables = pure_literals(new_sigma, variables)
        new_sigma = assign_simplify(new_sigma, new_variables)
        new_sigma, new_variables = unit_clause(new_sigma, new_variables)
        new_sigma = assign_simplify(new_sigma, new_variables)

    # TODO make a more robust check
    if diff_shape(new_sigma, sigma):
        return dpll(new_sigma, new_variables)

    # Split with recursive call if needed
    else:
        print("SPLIT")
        # Choose a predicate (randomly)
        predicate = choice(list(set([y for x in sigma for y in x])))
        # Choose a value (randomly)
        val = choice([True, False])
        # Set predicate to value and recurse
        variables[predicate] = val
        new_sigma = assign_simplify(new_sigma, variables)

        return dpll(new_sigma, variables)


def diff_shape(a, b):
    """Compare shape of two nested lists"""

    # print(f'Comparing: {a} and {b}')
    shape_a = (len(a), len([y for x in a for y in x]))
    shape_b = (len(a), len([y for x in b for y in x]))

    if shape_a == shape_b:
        return False
    else:
        return True


def assign_simplify(sigma, values):
    """Assigns values to an expression and simplifies
    """

    new_sigma = []

    for clause in sigma:
        new_clause = []
        for lit in clause:
            if lit in [True, False]:
                new_clause.append(lit)
            elif values[lit] is not None:
                new_clause.append(values[lit])
            else:
                new_clause.append(lit)
        if clause.count(True) is 0:  # Keep only if clause contains no `True`
            new_sigma.append(new_clause)
    return new_sigma


def verify_sat(sigma, end_values):
    """Verifies that found values do satisfy expression
    """
    # TODO
    out = assign_simplify(sigma, end_values)



if __name__ == '__main__':
    import rule_io
    sigma = rule_io.read_rules(
        'sudoku-rules.txt')
    sigma2 = rule_io.read_rules('sudoku-example.txt')
    sigma.extend(sigma2)
    initial_sigma = sigma
    collapsed = [y for x in sigma for y in x]
    variables = {k: None for k in list(set(collapsed))}
    dpll(sigma, variables)
