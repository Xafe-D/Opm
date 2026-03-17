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
        # Only apply when a single additive factor is being distributed.
        from sympy import Mul, Add, Pow

        if not isinstance(expr, Mul):
            return expr

        add_factors = [arg for arg in expr.args if isinstance(arg, Add)]
        pow_add = [arg for arg in expr.args if isinstance(arg, Pow) and isinstance(arg.base, Add) and arg.exp.is_number and arg.exp > 0]

        if len(add_factors) == 1:
            # Use SymPy's expand to distribute multiplication over addition
            # This handles cases like 2*(x+3) → 2*x + 2*3
            expanded = sympy.expand(expr)
            # Only return the expanded form if it's different
            if expanded != expr:
                return expanded
            return expr
        elif pow_add:
            # Handle cases like 2*(x+1)^2 → expand the power
            expanded = sympy.expand(expr)
            if expanded != expr:
                return expanded
            return expr

        return expr
    except:
        return expr
