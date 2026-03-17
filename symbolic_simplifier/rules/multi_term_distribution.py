"""
Multi-Term Distribution Rule Module

Handles expansion of products involving multiple terms.
Applies distributive property across complex expressions.

Functions:
    - apply_rule(): Apply multi-term distribution to an expression
"""

import sympy


def apply_rule(expr):
    """Apply multi-term distribution rule to the expression.

    Expands complex products, e.g.:
    (x+1)(x+2) → x^2 + 3x + 2
    (a+b)(c+d) → ac + ad + bc + bd

    Args:
        expr: SymPy expression to simplify

    Returns:
        Expression with multi-term products fully expanded
    """
    try:
        # We want to expand multi-term products such as (x+1)(x+2) even when they
        # are nested inside larger sums (e.g., 2*(x+1)*(x+2) + (x+1)**2).
        # However, avoid expanding expressions that represent rational forms
        # where cancellation is expected (e.g., (x+1)(x-1)/(x-1)).
        from sympy import Mul, Add, Pow

        def should_expand(mul_expr):
            if not isinstance(mul_expr, Mul):
                return False
            # Avoid expanding when the expression includes a denominator factor
            # (i.e., a power with negative exponent).
            if any(isinstance(arg, Pow) and arg.exp.is_Number and arg.exp < 0 for arg in mul_expr.args):
                return False
            add_factors = [arg for arg in mul_expr.args if isinstance(arg, Add)]
            return len(add_factors) > 1

        # Apply expansion recursively to all subexpressions.
        expanded = expr
        for sub in sympy.preorder_traversal(expr):
            if should_expand(sub):
                expanded = expanded.xreplace({sub: sympy.expand(sub)})

        return expanded
    except Exception:
        return expr
