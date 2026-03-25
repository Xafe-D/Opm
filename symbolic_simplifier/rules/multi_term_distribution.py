"""
Multi-Term Distribution Rule Module

Handles expansion of products involving multiple terms.
Applies distributive property across complex expressions.

Functions:
    - apply_rule(): Apply multi-term distribution to an expression
"""

import sympy


def apply_rule(expr):
    """Apply multi-term distribution rule to the expression.

    Expands complex products, e.g.:
    (x+1)(x+2) → x^2 + 3x + 2
    (a+b)(c+d) → ac + ad + bc + bd

    Args:
        expr: SymPy expression to simplify

    Returns:
        Expression with multi-term products fully expanded
    """
    try:
        # We want to expand multi-term products such as (x+1)(x+2) even when they
        # are nested inside larger sums (e.g., 2*(x+1)*(x+2) + (x+1)**2).
        # However, avoid expanding expressions that represent rational forms
        # where cancellation is expected (e.g., (x+1)(x-1)/(x-1)).
        from sympy import Mul, Add, Pow

        from .special_products import _is_special_product

        def should_expand(mul_expr):
            if not isinstance(mul_expr, Mul):
                return False
            if _is_special_product(mul_expr):
                return False
            # Avoid expanding when the expression includes a denominator factor
            # (i.e., a power with negative exponent).
            if any(isinstance(arg, Pow) and arg.exp.is_Number and arg.exp < 0 for arg in mul_expr.args):
                return False
            add_factors = [arg for arg in mul_expr.args if isinstance(arg, Add)]
            return len(add_factors) > 1

            # For top-level Add, expand each product term independently and keep unfused addition
        def _expand_mul_without_combining(mul_expr):
            # Expand a mul expression by distributing all Add factors,
            # preserving separate additive terms (no coefficient combination yet).
            from itertools import product

            add_factors = [arg for arg in mul_expr.args if isinstance(arg, sympy.Add)]
            other_factors = [arg for arg in mul_expr.args if not isinstance(arg, sympy.Add)]

            all_terms = []
            for combination in product(*(af.args for af in add_factors)):
                factors = other_factors + list(combination)
                if len(factors) == 1:
                    term = factors[0]
                else:
                    term = sympy.Mul(*factors, evaluate=False)
                # Keep terms expanded at term-level (x*x -> x**2, x*3 -> 3*x) but
                # keep the sum as separate additive pieces to preserve learning steps.
                term = sympy.expand(term)
                all_terms.append(term)

            return sympy.Add(*all_terms, evaluate=False)

        if isinstance(expr, sympy.Add):
            terms = []
            resolved = False
            for term in expr.args:
                if isinstance(term, sympy.Mul) and should_expand(term):
                    expanded_term = _expand_mul_without_combining(term)
                    if isinstance(expanded_term, sympy.Add):
                        for e in expanded_term.args:
                            terms.append(e)
                    else:
                        terms.append(expanded_term)
                    resolved = True
                else:
                    terms.append(term)

            if resolved:
                return sympy.Add(*terms, evaluate=False)
            return expr

        # Non-add expression expansion (nested product)
        if isinstance(expr, sympy.Mul) and should_expand(expr):
            expanded_expr = _expand_mul_without_combining(expr)
            if isinstance(expanded_expr, sympy.Add):
                return sympy.Add(*expanded_expr.args, evaluate=False)
            return expanded_expr

        return expr
    except Exception:
        return expr
