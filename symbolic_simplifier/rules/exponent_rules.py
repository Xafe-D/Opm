"""
Exponent Rules Module

Handles simplification of expressions involving exponents.
Rules: product of powers, power of power, quotient of powers, etc.

Functions:
    - apply_rule(): Apply exponent simplification rules to an expression
"""

import sympy


def _needs_base_simplification(expr):
    from sympy import Pow, Add
    from collections import Counter

    if isinstance(expr, Pow) and isinstance(expr.base, Add):
        term_signatures = []
        for term in expr.base.args:
            coeff, factors = term.as_coeff_mul()
            monomial = tuple(sorted(str(f) for f in factors))
            term_signatures.append(monomial)

        counts = Counter(term_signatures)
        if any(count > 1 for count in counts.values()):
            # Example: (x + x)**2 or (2*x + x)**2 needs base simplification.
            return True

    return any(_needs_base_simplification(arg) for arg in getattr(expr, "args", []))


def _simplify_powers(expr):
    from sympy import Add, Mul, Pow, Integer

    if isinstance(expr, Pow):
        base = _simplify_powers(expr.base)
        exp = _simplify_powers(expr.exp)

        if isinstance(base, Pow):
            combined_exp = base.exp * exp
            return sympy.Pow(base.base, combined_exp, evaluate=False)

        if exp == 1:
            return base
        if exp == 0:
            return Integer(1)

        return sympy.Pow(base, exp, evaluate=False)

    if isinstance(expr, Mul):
        return sympy.Mul(*[_simplify_powers(arg) for arg in expr.args], evaluate=False)

    if isinstance(expr, Add):
        return sympy.Add(*[_simplify_powers(arg) for arg in expr.args], evaluate=False)

    if getattr(expr, "args", None):
        args = [_simplify_powers(arg) for arg in expr.args]
        try:
            return expr.func(*args, evaluate=False)
        except TypeError:
            return expr.func(*args)

    return expr


def apply_rule(expr, warning_callback=None):
    """Apply exponent rules to the expression.

    Applies exponent simplification rules:
    - Power rule: (a^b)^c = a^(b*c)
    - Zero rule: a^0 = 1
    - One rule: a^1 = a

    Args:
        expr: SymPy expression to simplify
        warning_callback: Optional callable that accepts a warning string

    Returns:
        Expression with exponent rules applied
    """
    try:
        if _needs_base_simplification(expr):
            if warning_callback is not None:
                warning_callback(
                    "⚠️ WARNING: Simplify the base using Combine Like Terms before applying Exponent Rules."
                )
            return expr

        if not expr.has(sympy.Pow):
            return expr

        simplified = _simplify_powers(expr)
        if simplified != expr:
            return simplified

        return expr
    except:
        return expr
