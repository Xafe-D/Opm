import sympy as sp

expr = sp.sympify('2*(x+1)*(x+2) + (x+1)**2', evaluate=False)

# replicate has_multi_term_distribution from engine.py

def has_multi_term_distribution(e):
    from sympy import Mul, Add
    if isinstance(e, Mul):
        add_factors = [arg for arg in e.args if isinstance(arg, Add)]
        return len(add_factors) > 1
    return any(has_multi_term_distribution(arg) for arg in getattr(e, 'args', []))

print('expr:', expr)
print('type:', type(expr))
print('has_multi_term_distribution:', has_multi_term_distribution(expr))
