"""Factorization Rule Module

Handles general factorization of polynomial expressions.

Functions:
    - apply_rule(): Apply factorization to an expression
"""

import sympy


def apply_rule(expr):
    """Apply factorization to the expression.

    Uses SymPy's factor() to factor polynomials when possible.

    Args:
        expr: SymPy expression to simplify

    Returns:
        Expression with factorization applied
    """
    try:
        factored = sympy.factor(expr)
        if factored != expr:
            return factored
        return expr
    except:
        return expr
