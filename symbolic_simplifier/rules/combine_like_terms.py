"""
Combine Like Terms Rule Module

Handles combining and simplifying like terms in algebraic expressions.
Combines coefficients of identical variables and terms.

Functions:
    - apply_rule(): Apply combine like terms to an expression
"""

import sympy


def _has_locked_terms(expr):
    from sympy import Add, Mul, Pow

    if isinstance(expr, Pow) and isinstance(expr.base, Add):
        return True

    if isinstance(expr, Mul):
        if any(isinstance(arg, Add) for arg in expr.args):
            return True

    return any(_has_locked_terms(arg) for arg in getattr(expr, "args", []))


def apply_rule(expr, warning_callback=None):
    """Apply combine like terms rule to the expression.

    Combines coefficients of identical terms, e.g.:
    3x + 2x → 5x
    x^2 + 3x^2 → 4x^2

    If variables are locked inside parentheses with a multiplier or exponent,
    do not simplify and optionally log a robustness warning.

    Args:
        expr: SymPy expression to simplify
        warning_callback: Optional callable that accepts a warning string

    Returns:
        Expression with like terms combined
    """
    try:
        if _has_locked_terms(expr):
            if warning_callback is not None:
                warning_callback(
                    "⚠️ RECOMMENDED: Use Binomial Expansion and Distributive Property panels first to unlock terms for combining."
                )
            return expr

        # Combine constant-only additive expressions first (e.g., 5 + 3 -> 8)
        if expr.is_Add and expr.free_symbols == set():
            combined_value = sympy.simplify(expr)
            return combined_value

        # Only combine like terms on a top-level additive expression.
        if not isinstance(expr, sympy.Add):
            return expr

        # If any term contains an unexpanded additive subexpression,
        # flatten recursively before combining so we can show an explicit combine step.
        def _flatten_add(a):
            if not isinstance(a, sympy.Add):
                return a
            flat_args = []
            for term in a.args:
                expanded_term = _flatten_add(term)
                if isinstance(expanded_term, sympy.Add):
                    flat_args.extend(expanded_term.args)
                else:
                    flat_args.append(expanded_term)
            return sympy.Add(*flat_args, evaluate=False)

        if any(term.has(sympy.Add) for term in expr.args):
            expr = _flatten_add(expr)

        # Expand to a canonical add-term representation (without factoring)
        expanded = sympy.expand(expr)
        if not isinstance(expanded, sympy.Add):
            # could be constant like 7 or single term
            return expanded

        # Use Poly to combine like terms without factoring to product form
        symbols = sorted(expanded.free_symbols, key=lambda s: str(s))
        if not symbols:
            # no symbols but Add with constants should've been simplified above
            return expanded

        poly = sympy.Poly(expanded, *symbols)
        combined = poly.as_expr()

        return combined if combined != expr else expr
    except Exception:
        # on error, preserve expression unchanged to avoid hidden simplification
        return expr

