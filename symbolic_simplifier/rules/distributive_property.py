"""
Distributive Property Rule Module

Implements the distributive property: a(b + c) = ab + ac

Functions:
    - apply_rule(): Apply distributive property to an expression
"""

import sympy


def apply_rule(expr, raw_input=None):
    """Apply distributive property rule to the expression.

    Expands multiplication over addition/subtraction, e.g.:
    2(x + 3) → 2x + 6
    a(b + c + d) → ab + ac + ad

    Args:
        expr: SymPy expression to simplify
        raw_input: Original string input for pattern detection

    Returns:
        Expression with distributive property applied
    """
    try:
        # Use SymPy's expand_mul to distribute multiplication over addition
        # This handles cases like 2*(x+3) → 2*x + 2*3
        expanded = sympy.expand_mul(expr)

        # Only return the expanded form if it's different
        if expanded != expr:
            return expanded

        return expr
    except:
        return expr
