"""
Rational Simplification Rule Module

Handles simplification of rational expressions (fractions).
Factors numerator and denominator, then cancels common factors.

Functions:
    - apply_rule(): Apply rational simplification to an expression
"""

import sympy


def apply_rule(expr, steps=None):
    """Apply rational simplification rule to the expression.

    Simplifies rational expressions by:
    1. Factoring numerator and denominator
    2. Canceling common factors
    3. Simplifying the resulting fraction

    Examples:
    (x^2 - 1)/(x - 1) → (x+1)(x-1)/(x-1) → x+1
    (2x + 4)/6 → 2(x+2)/6 → (x+2)/3

    Args:
        expr: SymPy expression to simplify
        steps: Optional list to append step descriptions

    Returns:
        Simplified rational expression with common factors canceled
    """
    try:
        # Only treat expressions that are true fractions (denominator other than 1).
        # Polynomials count as rational functions in SymPy, but we don't want to
        # expand them as part of "rational simplification".
        num, den = expr.as_numer_denom()
        if den == 1:
            # nothing to cancel, leave polynomial alone
            return expr

        # additionally guard against non‑rational‑function cases
        if not expr.is_rational_function():
            return expr

        # Use SymPy's cancel to simplify rational expressions
        # This automatically factors and cancels common terms
        canceled = sympy.cancel(expr)

        # Also try simplify for additional simplification
        simplified = sympy.simplify(canceled)

        # Return the most simplified form
        if simplified != expr:
            return simplified
        elif canceled != expr:
            return canceled

        return expr
    except:
        return expr
