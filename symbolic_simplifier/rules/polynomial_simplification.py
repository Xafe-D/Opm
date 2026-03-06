"""
Polynomial Simplification Rule Module

Handles polynomial-specific simplifications.
Combines terms, arranges by degree, standard form conversions.

Functions:
    - apply_rule(): Apply polynomial simplification to an expression
"""

import sympy


def apply_rule(expr):
    """Apply polynomial simplification rule to the expression.

    Performs polynomial-specific operations:
    - Combines like terms
    - Arranges terms by descending degree
    - Converts to standard polynomial form
    - Removes zero coefficients

    Examples:
    x^2 + 3x + 2x^2 → 3x^2 + 3x (combine like terms)
    x + x^2 → x^2 + x (arrange by degree)

    Args:
        expr: SymPy expression (should be polynomial)

    Returns:
        Simplified polynomial in standard form
    """
    try:
        # Check if expression is a polynomial
        if not expr.is_polynomial():
            return expr

        # Use SymPy's Poly class for polynomial operations
        # This provides better polynomial manipulation
        poly = sympy.Poly(expr)

        # Get the polynomial in standard form (expanded and collected)
        standard_form = poly.as_expr()

        # Also try to collect terms by variables
        collected = sympy.collect(standard_form, expr.free_symbols, evaluate=True)

        # Use simplify for final cleanup
        simplified = sympy.simplify(collected)

        # Return the most appropriate form
        if simplified != expr:
            return simplified
        elif collected != expr:
            return collected
        elif standard_form != expr:
            return standard_form

        return expr
    except:
        # Fallback to basic simplification if polynomial operations fail
        return sympy.simplify(expr)
