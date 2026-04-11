"""Factorization Rule Module

Handles general factorization of polynomial expressions.

Functions:
    - apply_rule(): Apply factorization to an expression
"""

import sympy


def _has_unexpanded_products(expr):
    from sympy import Add, Mul

    if isinstance(expr, Add):
        for term in expr.args:
            if isinstance(term, Mul) and any(isinstance(arg, Add) for arg in term.args):
                return True
    if isinstance(expr, Mul):
        if any(isinstance(arg, Add) for arg in expr.args):
            return True

    return any(_has_unexpanded_products(arg) for arg in getattr(expr, "args", []))


def apply_rule(expr, warning_callback=None):
    """Apply factorization to the expression.

    Uses SymPy's factor() to factor polynomials when possible.

    If the expression contains unexpanded products or is not in standard
    polynomial form, a warning can be logged and the expression is preserved.

    Args:
        expr: SymPy expression to simplify
        warning_callback: Optional callable that accepts a warning string

    Returns:
        Expression with factorization applied
    """
    try:
        if not expr.is_polynomial():
            if warning_callback is not None:
                warning_callback(
                    "⚠️ WARNING: Factorization requires a polynomial expression in standard form. Use Rational Simplification or Exponent Rules first."
                )
            return expr

        if _has_unexpanded_products(expr):
            if warning_callback is not None:
                warning_callback(
                    "⚠️ WARNING: Expression contains unexpanded products. Apply Distributive Property or Multi-Term Distribution first before Factorization."
                )
            return expr

        factored = sympy.factor(expr)
        if factored != expr:
            if isinstance(factored, sympy.Mul):
                return sympy.Mul(*factored.args, evaluate=False)
            if isinstance(factored, sympy.Pow):
                return sympy.Pow(factored.base, factored.exp, evaluate=False)
            return factored
        return expr
    except:
        return expr
