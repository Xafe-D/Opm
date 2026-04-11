"""
Polynomial Simplification Rule Module

Handles polynomial-specific simplifications.
Combines terms, arranges by degree, standard form conversions.

Functions:
    - apply_rule(): Apply polynomial simplification to an expression
"""

import sympy


def _contains_non_polynomial_elements(expr):
    from sympy import Pow

    # Detect explicit negative exponents or fractional denominators.
    if isinstance(expr, Pow) and expr.exp.is_Number and expr.exp.is_negative:
        return True

    num, den = expr.as_numer_denom()
    if den != 1:
        return True

    return any(_contains_non_polynomial_elements(arg) for arg in getattr(expr, "args", []))


def apply_rule(expr, warning_callback=None):
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
        warning_callback: Optional callable that accepts a warning string

    Returns:
        Simplified polynomial in standard form
    """
    try:
        from sympy import Add, Mul
        
        if _contains_non_polynomial_elements(expr):
            if warning_callback is not None:
                warning_callback(
                    "⚠️ WARNING: Non-polynomial elements detected. Please use Rational Simplification or Exponent Rules for this input."
                )
            return expr

        if not expr.is_polynomial():
            if warning_callback is not None:
                warning_callback(
                    "⚠️ WARNING: Polynomial Simplification requires a polynomial expression. Use Factorization or Special Products if needed."
                )
            return expr

        for subexpr in expr.atoms(Mul):
            add_count = sum(1 for arg in subexpr.args if isinstance(arg, Add))
            if add_count > 1:
                if warning_callback is not None:
                    warning_callback(
                        "⚠️ WARNING: The expression contains unexpanded products. Use Multi-Term Distribution before Polynomial Simplification."
                    )
                return expr

        terms = list(expr.args) if isinstance(expr, sympy.Add) else [expr]
        term_map = {}
        degree_order = []

        for term in terms:
            coeff, factors = term.as_coeff_mul()
            if len(factors) == 0:
                key = sympy.Integer(1)
            elif len(factors) == 1:
                key = factors[0]
            else:
                key = sympy.Mul(*factors, evaluate=False)

            if key in term_map:
                term_map[key] += coeff
            else:
                term_map[key] = coeff
                degree_order.append((key, sympy.degree(term, *expr.free_symbols)))

        simplified_terms = []
        for key, _ in sorted(degree_order, key=lambda item: (-item[1], str(item[0]))):
            coeff = term_map[key]
            if coeff == 0:
                continue
            if key == 1:
                simplified_terms.append(coeff)
            elif coeff == 1:
                simplified_terms.append(key)
            elif coeff == -1:
                simplified_terms.append(sympy.Mul(-1, key, evaluate=False))
            else:
                simplified_terms.append(sympy.Mul(coeff, key, evaluate=False))

        if not simplified_terms:
            return sympy.Integer(0)
        if len(simplified_terms) == 1:
            return simplified_terms[0]

        return sympy.Add(*simplified_terms, evaluate=False)
    except:
        return expr
