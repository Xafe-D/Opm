"""
Rational Simplification Rule Module

Handles simplification of rational expressions (fractions).
Factors numerator and denominator, then cancels common factors.

Functions:
    - apply_rule(): Apply rational simplification to an expression
"""

import sympy


def _has_factorable_polynomial(expr):
    try:
        factored = sympy.factor(expr)
        return factored != expr
    except Exception:
        return False


def apply_rule(expr, steps=None, warning_callback=None):
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
        warning_callback: Optional callable that accepts a warning string

    Returns:
        Simplified rational expression with common factors canceled
    """
    try:
        num, den = expr.as_numer_denom()
        if den == 1:
            if warning_callback is not None:
                warning_callback(
                    "⚠️ WARNING: Rational Simplification requires a non-trivial fraction. Use Factorization or Special Products first."
                )
            return expr

        if not expr.is_rational_function():
            if warning_callback is not None:
                warning_callback(
                    "⚠️ WARNING: The input is not a rational function. Use Polynomial Simplification or Factorization first."
                )
            return expr

        if (num.is_polynomial() and _has_factorable_polynomial(num)) or (
            den.is_polynomial() and _has_factorable_polynomial(den)
        ):
            if warning_callback is not None:
                warning_callback(
                    "⚠️ WARNING: Complex polynomial factors are present. Apply Factorization or Special Products before Rational Simplification."
                )

        canceled = sympy.cancel(expr)
        if canceled == expr:
            return expr

        num_c, den_c = canceled.as_numer_denom()
        if den_c == 1:
            return num_c

        return sympy.Mul(num_c, sympy.Pow(den_c, -1), evaluate=False)
    except:
        return expr
