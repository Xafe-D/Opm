"""
Parser Module

Handles parsing and validation of symbolic mathematical expressions.
Converts string input to SymPy expression objects.

Functions:
    - validate_expression(): Validate input expression syntax and safety
    - parse_expression(): Parse string to SymPy expression
"""

import re
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)


def validate_expression(expr: str):
    """Perform light-weight validation on the raw input string.

    **Rules:**
    1. Expression must not be empty.
    2. Maximum length is 200 characters (arbitrary safety cap).
    3. Only allowed characters may appear: letters, digits, underscore,
       whitespace and the operators ``+-*/^(),.``.  This covers variable names
       and common function names like ``sin``/``cos``/``log``.
    4. Parentheses must be balanced.

    Returns a tuple ``(valid: bool, message: str)``.  If ``valid`` is ``False``
    then ``message`` describes the first rule that failed.
    """
    if expr is None or not expr.strip():
        return False, "Expression is empty. Please provide a valid symbolic expression."
    if len(expr) > 200:
        return False, "Expression is too long (limit 200 characters)."
    # allowed characters pattern
    if not re.match(r"^[0-9A-Za-z_\s\+\-\*\/\^\(\)\.,]*$", expr):
        return False, "Expression contains invalid characters. Only letters, digits and +-*/^(),. are allowed."
    # balanced parentheses
    stack = []
    for ch in expr:
        if ch == "(":
            stack.append(ch)
        elif ch == ")":
            if not stack:
                return False, "Parentheses are not balanced."
            stack.pop()
    if stack:
        return False, "Parentheses are not balanced."
    return True, ""


def parse_expression(raw_expression: str):
    """Parse string expression to SymPy expression object.
    
    Args:
        raw_expression: String containing the mathematical expression
        
    Returns:
        SymPy expression object (with evaluate=False to preserve structure)
        
    Raises:
        Exception: If parsing fails
    """
    # allow implicit multiplication like '3x' or '(x+1)(x-1)'
    expr_str = raw_expression.replace("^", "**")
    transformations = standard_transformations + (implicit_multiplication_application,)
    # use evaluate=False to keep the structure intact (so we can later show how
    # terms were combined/factored rather than having SymPy do it immediately)
    expression = parse_expr(expr_str, transformations=transformations, evaluate=False)
    return expression
