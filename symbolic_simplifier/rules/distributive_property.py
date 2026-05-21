"""
Distributive Property Rule Module

Implements the distributive property: a(b + c) = ab + ac

Functions:
    - apply_rule(): Apply distributive property to an expression
"""

import sympy


def _contains_binomial_power(expr):
    from sympy import Pow, Add

    if isinstance(expr, Pow) and isinstance(expr.base, Add):
        return True

    return any(_contains_binomial_power(arg) for arg in getattr(expr, "args", []))


def apply_rule(expr, raw_input=None, warning_callback=None):
    """Apply distributive property rule to the expression.

    STRICT ENFORCEMENT: Only distributes a SINGLE term over a sum.
    
    Valid patterns:
    - 2(x + 3) → 2x + 6
    - a(b + c) → ab + ac
    - (coefficient or simple term) * (sum)
    
    INVALID patterns (rejected to Multi-Term Distribution):
    - (x+1)(x+2) → NOT distributive, this is multi-term distribution
    - (a+b)(c+d) → NOT distributive
    
    Args:
        expr: SymPy expression to simplify
        raw_input: Original string input for pattern detection
        warning_callback: Optional callable that accepts a warning string

    Returns:
        Expression with distributive property applied, or original if pattern doesn't match
    """
    try:
        if _contains_binomial_power(expr):
            if warning_callback is not None:
                warning_callback(
                    "⚠️ RECOMMENDED: Use Binomial Expansion Panel first before attempting distribution."
                )
            return expr

        from sympy import Mul, Add, Symbol

        # STRICT: Only apply to Mul where exactly ONE factor is an Add
        # All other factors must NOT be Adds (to exclude multi-term distribution)
        replacements = {}
        for subexpr in expr.atoms(Mul):
            add_count = sum(1 for arg in subexpr.args if isinstance(arg, Add))
            
            # Only apply distributive property if exactly ONE additive term
            if add_count == 1:
                non_add_args = [arg for arg in subexpr.args if not isinstance(arg, Add)]
                all_non_add_are_coefficients = all(
                    arg.is_number or (isinstance(arg, Symbol) and arg.is_symbol)
                    for arg in non_add_args
                )
                
                if all_non_add_are_coefficients:
                    add_term = next(arg for arg in subexpr.args if isinstance(arg, Add))
                    other_factors = [arg for arg in subexpr.args if not isinstance(arg, Add)]

                    distributed_terms = []
                    for term in add_term.args:
                        distributed_term = sympy.Mul(*other_factors, term, evaluate=False)
                        distributed_term = sympy.expand_mul(distributed_term)
                        distributed_terms.append(distributed_term)

                    expanded = sympy.Add(*distributed_terms, evaluate=False)
                    if expanded != subexpr:
                        replacements[subexpr] = expanded

        if not replacements:
            return expr

        if isinstance(expr, sympy.Add):
            new_terms = []
            for arg in expr.args:
                if arg in replacements:
                    replacement = replacements[arg]
                    if isinstance(replacement, sympy.Add):
                        new_terms.extend(replacement.args)
                    else:
                        new_terms.append(replacement)
                else:
                    new_terms.append(arg)
            return sympy.Add(*new_terms, evaluate=False)

        new_expr = expr.xreplace(replacements)
        if isinstance(new_expr, sympy.Add):
            return sympy.Add(*new_expr.args, evaluate=False)
        return new_expr if new_expr != expr else expr
    except Exception:
        return expr
