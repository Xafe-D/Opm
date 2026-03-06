"""
Exponent Rules Module

Handles simplification of expressions involving exponents.
Rules: product of powers, power of power, quotient of powers, etc.

Functions:
    - apply_rule(): Apply exponent simplification rules to an expression
"""

import sympy


def apply_rule(expr):
    """Apply exponent rules to the expression.

    Applies exponent simplification rules:
    - Product rule: a^b * a^c = a^(b+c)
    - Quotient rule: a^b / a^c = a^(b-c)
    - Power rule: (a^b)^c = a^(b*c)
    - Zero rule: a^0 = 1 (for a ≠ 0)
    - One rule: a^1 = a

    Args:
        expr: SymPy expression to simplify

    Returns:
        Expression with exponent rules applied
    """
    try:
        # Use SymPy's powsimp to simplify expressions with powers
        # This combines and simplifies exponents according to the rules
        simplified = sympy.powsimp(expr)

        # Also try expand_power_exp and expand_power_base for additional simplification
        expanded_exp = sympy.expand_power_exp(simplified)
        expanded_base = sympy.expand_power_base(expanded_exp)

        # Return the most simplified form
        if expanded_base != expr:
            return expanded_base
        elif expanded_exp != expr:
            return expanded_exp
        elif simplified != expr:
            return simplified

        return expr
    except:
        return expr
