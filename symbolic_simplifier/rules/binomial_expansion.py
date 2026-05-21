"""
Binomial Expansion Rule Module

Handles expansion of binomial expressions and powers of binomials.
(a + b)^n and variations

Functions:
    - apply_rule(): Apply binomial expansion to an expression
"""

import sympy


def _contains_binomial_power(expr):
    """Return True if expr contains a binomial power (a + b)^n with n>1."""

    from sympy import Pow, Add

    if isinstance(expr, Pow) and isinstance(expr.base, Add) and expr.exp.is_Integer and expr.exp > 1:
        return True

    return any(_contains_binomial_power(arg) for arg in getattr(expr, "args", []))


def _expand_binomial_only(expr):
    from sympy import Add, Mul, Pow

    if isinstance(expr, Pow) and isinstance(expr.base, Add) and expr.exp.is_Integer and expr.exp > 1:
        expanded = sympy.expand(expr)
        return Add(*expanded.args, evaluate=False)

    if isinstance(expr, Mul):
        args = [_expand_binomial_only(a) for a in expr.args]
        return Mul(*args, evaluate=False)

    if isinstance(expr, Add):
        args = [_expand_binomial_only(a) for a in expr.args]
        return Add(*args, evaluate=False)

    if isinstance(expr, Pow):
        base = _expand_binomial_only(expr.base)
        return Pow(base, expr.exp, evaluate=False)

    if hasattr(expr, "args") and expr.args:
        args = [_expand_binomial_only(a) for a in expr.args]
        return expr.func(*args, evaluate=False)

    return expr


def apply_rule(expr, warning_callback=None):
    """Apply binomial expansion rule to the expression.

    Expands powers of binomials using binomial theorem, e.g.:
    (x + 1)^2 → x^2 + 2x + 1
    (a + b)^3 → a^3 + 3a^2b + 3ab^2 + b^3

    If the expression is a single term or already in standard polynomial form,
    the rule does not apply and a warning can be logged.

    Args:
        expr: SymPy expression to simplify
        warning_callback: Optional callable that accepts a warning string

    Returns:
        Expression with binomial expansions applied
    """
    try:
        if not _contains_binomial_power(expr):
            if warning_callback is not None:
                warning_callback(
                    "⚠️ WARNING: No binomial power detected. Use Polynomial Simplification or Combine Like Terms instead."
                )
            return expr

        expanded = _expand_binomial_only(expr)

        if expanded != expr:
            return expanded

        return expr
    except:
        return expr
