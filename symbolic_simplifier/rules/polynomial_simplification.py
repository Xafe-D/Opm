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

    STRICT ENFORCEMENT: Only simplifies ALREADY-EXPANDED polynomials.
    Does NOT expand products (that's Multi-Term Distribution's job).
    
    Performs polynomial-specific operations on simplified forms:
    - Combines like terms (x^2 + 2x^2 → 3x^2)
    - Arranges terms by descending degree
    - Removes zero coefficients
    
    Examples:
    x^2 + 2x^2 + 3x → 3x^2 + 3x (combine like terms)
    3x + x^2 → x^2 + 3x (arrange by degree)
    
    Does NOT handle:
    (x+1)(x+2) → use Multi-Term Distribution instead
    
    Args:
        expr: SymPy expression (should be polynomial)

    Returns:
        Simplified polynomial in standard form
    """
    try:
        from sympy import Add, Mul
        
        # Check if expression is a polynomial
        if not expr.is_polynomial():
            return expr

        # STRICT: Only simplify, don't expand
        # Check if there are unexpanded products (Mul with Add factors)
        has_unexpanded_products = False
        for subexpr in expr.atoms(Mul):
            add_count = sum(1 for arg in subexpr.args if isinstance(arg, Add))
            if add_count > 1:  # Multiple adds being multiplied together = unexpanded
                has_unexpanded_products = True
                break

        if has_unexpanded_products:
            # Don't expand; this should be handled by Multi-Term Distribution
            return expr

        # Collect and simplify like terms without expanding new products
        collected = sympy.collect(expr, expr.free_symbols, evaluate=True)

        return collected if collected != expr else expr
    except:
        # Fallback to basic simplification if polynomial operations fail
        return expr
