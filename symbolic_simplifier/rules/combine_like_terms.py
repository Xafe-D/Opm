"""
Combine Like Terms Rule Module

Handles combining and simplifying like terms in algebraic expressions.
Combines coefficients of identical variables and terms.

Functions:
    - apply_rule(): Apply combine like terms to an expression
"""

import sympy


def apply_rule(expr):
    """Apply combine like terms rule to the expression.

    Combines coefficients of identical terms, e.g.:
    3x + 2x → 5x
    x^2 + 3x^2 → 4x^2

    Args:
        expr: SymPy expression to simplify

    Returns:
        Expression with like terms combined
    """
    # Use SymPy's collect and simplify to combine like terms
    # collect() groups terms by their variables
    # simplify() combines coefficients
    try:
        # First try to collect terms by variables
        collected = sympy.collect(expr, expr.free_symbols, evaluate=True)
        # Then simplify to combine coefficients
        simplified = sympy.simplify(collected)
        return simplified
    except:
        # Fallback to basic simplify if collect fails
        return sympy.simplify(expr)

