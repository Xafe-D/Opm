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
    try:
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

