import random

def generate_smt2_3cnf(num_vars, num_clauses):
    variables = [f"x{i}" for i in range(1, num_vars+1)]
    clauses = []
    for _ in range(num_clauses):
        clause = [random.choice([f'{var}' if random.getrandbits(1) else f'(not {var})' for var in variables]) for _ in range(3)]
        clauses.append(f'(or {" ".join(clause)})')

    declare_str = '\n'.join([f'(declare-const {var} Bool)' for var in variables])
    clause_str = "\n".join(clauses)
    formula = declare_str + "\n\n" + "(assert (and\n" + clause_str + "\n))"

    with open(f"3cnf-{num_vars}-{num_clauses}.smt2", 'w') as file:
        file.write(formula)

if __name__ == "__main__":
    generate_smt2_3cnf(10, 20)