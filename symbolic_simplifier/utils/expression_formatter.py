"""
Expression Formatter Module

Handles formatting and beautification of mathematical expressions.
Converts SymPy output to human-readable mathematical notation.

Functions:
    - beautify_str(): Convert SymPy strings to conventional math notation
    - format_trail(): Format the complete simplification trail
"""

import re


def beautify_str(s: str) -> str:
    """Convert a SymPy string into a more conventional math notation.

    - replace the Python power operator `**` with caret `^`.
    - drop multiplication stars where they are purely syntactic (e.g. between a
      symbol and a coefficient) but **not** between two digits (``1*4`` should
      remain ``4`` after simplification, not ``14``).

    This function is intended for display only; it does **not** modify the
    underlying expression objects.
    """
    # first convert power operator
    s = s.replace("**", "^")
    # remove stars except those between digits
    # pattern: star not bordered by digits on both sides
    s = re.sub(r"(?<!\d)\*(?!\d)", "", s)
    # strip explicit multiplication by 1 which can appear after parsing with
    # evaluate=False (e.g. 1*4, 1*x, x*1).  Use word boundaries to avoid
    # mangling numbers like 21*3.
    s = re.sub(r"\b1\*", "", s)
    s = re.sub(r"\*1\b", "", s)
    return s


def format_trail(trail: dict) -> str:
    """Format the complete simplification trail into human-readable output.
    
    Args:
        trail: Dictionary containing the simplification steps and metadata
        
    Returns:
        Formatted string with all steps, verification, and summary
    """
    from sympy.parsing.sympy_parser import (
        parse_expr,
        standard_transformations,
        implicit_multiplication_application,
    )
    
    lines = []

    # GIVEN
    lines.append("GIVEN")
    lines.append(f"Problem: Simplify the symbolic expression")
    lines.append(f"Input Expression: {trail['given']}")
    try:
        expr_str = trail['given'].replace("^", "**")
        transformations = standard_transformations + (implicit_multiplication_application,)
        sym_expr = parse_expr(expr_str, transformations=transformations, evaluate=False)
        vars_detected = sorted([str(s) for s in sym_expr.free_symbols])
        lines.append(f"Detected Variables: {', '.join(vars_detected)}")
    except:
        lines.append("Detected Variables: N/A")
    lines.append("")

    # METHOD
    lines.append("METHOD")
    # Show the new detailed method section, which lists applied rules
    method_lines = trail["method"].split("\n")
    for mline in method_lines:
        lines.append(mline)
    lines.append("")



    # STEPS
    lines.append("STEPS")
    for step in trail["steps"]:
        lines.append(step)
    lines.append("")

    # FINAL
    lines.append("FINAL ANSWER")
    lines.append(f"Factored Form: {trail['factored_form']}")
    lines.append(f"Canonical Simplified Form: {trail['canonical_form']}")
    if trail.get("log_note"):
        lines.append(trail["log_note"])
    lines.append("")

    # VERIFICATION
    lines.append("VERIFICATION")
    lines.append(trail["verification"])
    lines.append("")

    # SUMMARY
    lines.append("SUMMARY")
    lines.append(trail["summary"])

    return "\n".join(lines)
