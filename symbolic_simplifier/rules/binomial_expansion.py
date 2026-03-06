"""
Binomial Expansion Rule Module

Handles expansion of binomial expressions and powers of binomials.
(a + b)^n and variations

Functions:
    - apply_rule(): Apply binomial expansion to an expression
"""

import sympy


def apply_rule(expr):
    """Apply binomial expansion rule to the expression.

    Expands powers of binomials using binomial theorem, e.g.:
    (x + 1)^2 → x^2 + 2x + 1
    (a + b)^3 → a^3 + 3a^2b + 3ab^2 + b^3

    Args:
        expr: SymPy expression to simplify

    Returns:
        Expression with binomial expansions applied
    """
    try:
        # Use SymPy's expand to handle binomial expansion
        # This automatically applies the binomial theorem
        expanded = sympy.expand(expr)

        # Only return if expansion actually changed the expression
        if expanded != expr:
            return expanded

        return expr
    except:
        return expr
