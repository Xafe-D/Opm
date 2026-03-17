import sympy as sp
from symbolic_simplifier.engine import detect_method

expr = sp.sympify('2*(x+1)*(x+2) + (x+1)**2', evaluate=False)
from symbolic_simplifier.engine import detect_method
from symbolic_simplifier.engine import has_multi_term_distribution

print('has_multi_term_distribution:', has_multi_term_distribution(expr))
method, steps = detect_method(expr)
print('methods:')
print('\n'.join(method))
print('steps:', steps)
