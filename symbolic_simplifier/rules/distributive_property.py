"""
Distributive Property Rule Module

Implements the distributive property: a(b + c) = ab + ac

Functions:
    - apply_rule(): Apply distributive property to an expression
"""

import sympy


def apply_rule(expr, raw_input=None):
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

    Returns:
        Expression with distributive property applied, or original if pattern doesn't match
    """
    try:
        from sympy import Mul, Add, Symbol

        # STRICT: Only apply to Mul where exactly ONE factor is an Add
        # All other factors must NOT be Adds (to exclude multi-term distribution)
        replacements = {}
        for subexpr in expr.atoms(Mul):
            add_count = sum(1 for arg in subexpr.args if isinstance(arg, Add))
            
            # Only apply distributive property if exactly ONE additive term
            if add_count == 1:
                # Verify all non-Add factors are non-symbolic or single terms
                non_add_args = [arg for arg in subexpr.args if not isinstance(arg, Add)]
                all_non_add_are_coefficients = all(
                    arg.is_number or (isinstance(arg, Symbol) and arg.is_symbol)
                    for arg in non_add_args
                )
                
                if all_non_add_are_coefficients:
                    expanded = sympy.expand(subexpr)
                    if expanded != subexpr:
                        replacements[subexpr] = expanded

        if not replacements:
            return expr

        new_expr = expr.xreplace(replacements)
        return new_expr if new_expr != expr else expr
    except Exception:
        return expr
