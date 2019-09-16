"""Implementation of DPLL algorithm"""

from simplifications import tautology, unit_clause, pure_literals
from random import choice
import copy

def dpll(sigma, variables):
    """Apply DPLL algorithm to some expression `sigma`

    sigma must be a list of lists of integers representing
    DIMACS notation for the problem.

    """
    # print(f'Sigma: {sigma}')
    print(
        f'DPLL: {len(sigma)} {len([x for x in list(variables.values()) if x is None])}')
    # if len(sigma) < 10:
    #     out = assign_simplify(sigma, variables)
    #     for i, clause in enumerate(out):
    #         print(f'Clause: {sigma[i]} -> {clause}')
    if len(sigma) < 1:
        print('SAT', sigma)
        print([x for x in variables.keys() if variables[x] == True])
        return True, variables
    elif [] in sigma:
        print('UNSAT')
        return False, variables
    # Simplify (tautologies, unit clauses, pure literals)
    else:
        old_sigma = [[]]
        new_sigma = copy.deepcopy(sigma)
        new_variables = copy.deepcopy(variables)
        new_sigma = tautology(new_sigma)
        new_sigma = assign_simplify(new_sigma, new_variables)
        while diff_shape(old_sigma, new_sigma) and len(new_sigma) > 1 and [] not in new_sigma:
            old_sigma = copy.deepcopy(new_sigma)
            print("SIMPLIFY...")
            # import pdb; pdb.set_trace()
            new_sigma, new_variables = pure_literals(new_sigma, new_variables)
            # print(f'Pure: {new_sigma}')
            # new_sigma = assign_simplify(new_sigma, new_variables)
            # print(new_sigma)
            new_sigma, new_variables = unit_clause(new_sigma, new_variables)
            # print(f'Unit: {new_sigma}')
            new_sigma = assign_simplify(new_sigma, new_variables)
            # print(f'Assign: {new_sigma}')

        if len(new_sigma) < 1 or [] in sigma:
            return dpll(new_sigma, new_variables)

        # Split with recursive call if needed
        sigma_pre_split = copy.deepcopy(new_sigma)
        # Choose a predicate (randomly) from unassigned variables
        predicate = choice([k for k in variables.keys() if variables[k] is None])
        # Choose a value (randomly)
        val = choice([True, False])
        # Set predicate to value and recurse
        new_variables[predicate] = val
        new_sigma = assign_simplify(new_sigma, variables)
        print(f"SPLIT: {predicate} = {val}")
        res, var = dpll(new_sigma, new_variables)
        if not res:
            print(f"BACKTRACK: {predicate} = {not val}")
            val = not val
            variables[predicate] = val
            new_sigma = assign_simplify(sigma_pre_split, variables)
            return dpll(sigma_pre_split, variables)
        else:
            return res, var


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
                if lit: new_clause.append(lit)
            elif values[abs(lit)] is not None:
                val = values[abs(lit)]
                sign = 1 if lit > 0 else -1
                lit_val = val if sign == 1 else (not val)
                if lit_val: new_clause.append(lit_val)
            else:
                new_clause.append(lit)
        if new_clause.count(True) is 0:  # Keep only if clause contains no `True`
            new_sigma.append(new_clause)
    return new_sigma


def verify_sat(sigma, end_values):
    """Verifies that found values satisfy expression
    """
    new_sigma = []
    for clause in sigma:
        new_clause = []
        for lit in clause:
            val = end_values[abs(lit)]
            if val is not None:
                new_clause.append(val)

    for i, clause in enumerate(new_sigma):
        if not any(clause):
            print(f'Clause {i} untrue: {sigma[i]} -> {clause}')
            return False
    return True


if __name__ == '__main__':
    import rule_io
    sigma = rule_io.read_rules(
        'sudoku-rules.txt')
    sigma2 = rule_io.read_rules('sudoku-example.txt')
    sigma.extend(sigma2)
    sigma.extend([[-318, -419]])
    initial_sigma = copy.deepcopy(sigma)
    collapsed = list(set([abs(y) for x in sigma for y in x]))
    variables = {k: None for k in collapsed}
    res, out_variables = dpll(sigma, variables)

    # import ipdb; ipdb.set_trace()
    print(verify_sat(sigma, out_variables))
