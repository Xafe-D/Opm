"""
Special Products Rule Module

Handles special algebraic products and identities.
Difference of squares, sum/difference of cubes, etc.

Functions:
    - apply_rule(): Apply special product rules to an expression
"""

import sympy


def _is_special_product(expr):
    """Return True if expr matches a strictly defined special product pattern."""

    from sympy import Wild, factor

    a = Wild("a")
    b = Wild("b")

    def _matches_special(e):
        if not e.free_symbols:
            return False
        if e.match((a - b) * (a + b)):
            return True
        if e.match((a + b) ** 2):
            return True
        if e.match((a - b) ** 2):
            return True
        return False

    # Check the expression itself first
    if _matches_special(expr):
        return True

    # For rational expressions, inspect numerator first as a special product
    try:
        num, den = expr.as_numer_denom()
        if den != 1:
            # If denominator is already an explicit factor of numerator as a Mul,
            # treat as rational simplification case (don't prioritize special product)
            if isinstance(num, sympy.Mul) and any(arg == den for arg in num.args):
                return False

            if _matches_special(num):
                return True
            try:
                num_factored = factor(num)
                if num_factored != num and _matches_special(num_factored):
                    return True
            except Exception:
                pass
    except Exception:
        pass

    # Check a strictly factored form that corresponds to special products
    try:
        f = factor(expr)
    except Exception:
        f = expr

    if f != expr and _matches_special(f):
        return True

    return False


def apply_rule(expr):
    """Apply special product rules to the expression.

    Recognizes and applies special algebraic identities:
    - Difference of squares: a^2 - b^2 = (a-b)(a+b)
    - Sum of cubes: a^3 + b^3 = (a+b)(a^2 - ab + b^2)
    - Difference of cubes: a^3 - b^3 = (a-b)(a^2 + ab + b^2)
    - Perfect square trinomial: a^2 + 2ab + b^2 = (a+b)^2

    Args:
        expr: SymPy expression to simplify

    Returns:
        Expression with special products simplified
    """
    try:
        if not _is_special_product(expr):
            return expr

        # For rational expressions, factor the numerator but do not cancel common factors yet.
        # This preserves distinct Special Products + Rational rules in the pipeline.
        num, den = expr.as_numer_denom()
        if den != 1 and _is_special_product(num):
            num_factored = sympy.factor(num)
            candidate = sympy.Mul(num_factored, sympy.Pow(den, -1), evaluate=False)
            if candidate != expr:
                return candidate

        factored = sympy.factor(expr)
        if factored != expr:
            return factored

        return expr
    except:
        return expr
