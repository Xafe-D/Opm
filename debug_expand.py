import sympy as sp
from symbolic_simplifier.rules.multi_term_distribution import apply_rule

expr = sp.sympify('(x+1)*(x+3)', evaluate=False)

# replicate logic to see which subexpressions are considered for expansion
from sympy import Mul, Add, Pow

def should_expand(mul_expr):
    if not isinstance(mul_expr, Mul):
        return False
    if any(isinstance(arg, Pow) and arg.exp.is_Number and arg.exp < 0 for arg in mul_expr.args):
        return False
    add_factors = [arg for arg in mul_expr.args if isinstance(arg, Add)]
    return len(add_factors) > 1

for sub in expr.preorder_traversal():
    if should_expand(sub):
        print('should expand:', sub)
        print('expanded:', sp.expand(sub))

print('apply_rule result:', apply_rule(expr))
