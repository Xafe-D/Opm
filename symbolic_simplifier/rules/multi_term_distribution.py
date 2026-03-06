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
        # Use SymPy's expand to handle multi-term distribution
        # This expands products like (x+1)(x+2) into x^2 + 3x + 2
        expanded = sympy.expand(expr)

        # Only return if expansion actually changed the expression
        if expanded != expr:
            return expanded

        return expr
    except:
        return expr
