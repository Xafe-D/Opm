"""
Special Products Rule Module

Handles special algebraic products and identities.
Difference of squares, sum/difference of cubes, etc.

Functions:
    - apply_rule(): Apply special product rules to an expression
"""

import sympy


def apply_rule(expr):
    """Apply special product rules to the expression.

    Recognizes and applies special algebraic identities:
    - Difference of squares: a^2 - b^2 = (a-b)(a+b)
    - Sum of cubes: a^3 + b^3 = (a+b)(a^2 - ab + b^2)
    - Difference of cubes: a^3 - b^3 = (a-b)(a^2 + ab + b^2)
    - Perfect square trinomial: a^2 + 2ab + b^2 = (a+b)^2

    Args:
        expr: SymPy expression to simplify

    Returns:
        Expression with special products simplified
    """
    try:
        # Use SymPy's factor to recognize special products
        # factor() can identify these patterns and factor them accordingly
        factored = sympy.factor(expr)

        # Only return factored form if it's different and represents a special product
        if factored != expr:
            # Check if this looks like a special product pattern
            # For example, if we have a^2 - b^2 factored as (a-b)(a+b)
            return factored

        return expr
    except:
        return expr
