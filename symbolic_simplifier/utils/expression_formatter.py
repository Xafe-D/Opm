"""
Expression Formatter Module

Handles formatting and beautification of mathematical expressions.
Converts SymPy output to human-readable mathematical notation.

Functions:
    - beautify_str(): Convert SymPy strings to conventional math notation
    - format_trail(): Format the complete simplification trail
"""

import re
from sympy import sstr


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


def beautify_expr(expr) -> str:
    """Convert a SymPy expression to a human-readable string.

    Uses a lightweight recursive printer for Add, Mul and Pow so that
    unevaluated expressions preserve student-facing order and binomial
    formatting.
    """
    from sympy import Add, Mul, Pow, Integer

    def format_term(term, parent=None):
        if isinstance(term, Add):
            text = format_add(term)
            return f"({text})" if isinstance(parent, Add) else text
        if isinstance(term, Mul):
            numerator_parts = []
            denominator_parts = []
            for arg in term.args:
                if isinstance(arg, Pow) and arg.exp == -1:
                    denominator_parts.append(arg.base)
                    continue
                text = format_term(arg, term)
                if isinstance(arg, Add):
                    text = f"({text})"
                numerator_parts.append(text)
            numerator = "*".join(numerator_parts) if numerator_parts else "1"
            if denominator_parts:
                denom_parts = []
                for denom in denominator_parts:
                    denom_text = format_term(denom, term)
                    if isinstance(denom, (Add, Mul)):
                        denom_text = f"({denom_text})"
                    denom_parts.append(denom_text)
                return f"{numerator} / {'*'.join(denom_parts)}"
            return "*".join(numerator_parts)
        if isinstance(term, Pow):
            if term.exp == -1:
                base_text = format_term(term.base)
                if isinstance(term.base, (Add, Mul)):
                    base_text = f"({base_text})"
                return f"1/{base_text}"
            base_text = format_term(term.base)
            if isinstance(term.base, (Add, Mul)):
                base_text = f"({base_text})"
            return f"{base_text}^{format_term(term.exp)}"
        text = sstr(term, order='none')
        return beautify_str(text)

    def join_terms(formatted_terms):
        result = ""
        for term_text in formatted_terms:
            if not result:
                result = term_text
            elif term_text.startswith("- "):
                result += f" - {term_text[2:]}"
            else:
                result += f" + {term_text}"
        return result

    def format_add(add_expr):
        if len(add_expr.args) == 2 and any(arg.is_Integer for arg in add_expr.args):
            left, right = add_expr.args
            if left.is_Integer and not right.is_Integer:
                if left < 0:
                    return f"{format_term(right, add_expr)} - {format_term(-left, add_expr)}"
                return f"{format_term(right, add_expr)} + {format_term(left, add_expr)}"
            if right.is_Integer and not left.is_Integer:
                if right < 0:
                    return f"{format_term(left, add_expr)} - {format_term(-right, add_expr)}"
                return f"{format_term(left, add_expr)} + {format_term(right, add_expr)}"
        non_constants = []
        constants = []
        for arg in add_expr.args:
            term_text = format_term(arg, add_expr)
            if arg.is_Number:
                constants.append(term_text)
            else:
                non_constants.append(term_text)
        if non_constants and constants:
            return join_terms(non_constants + constants)
        return join_terms(non_constants or constants)

    return format_term(expr)


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
    if trail.get("final_warning"):
        lines.append(trail["final_warning"])
    lines.append(f"Factored Form: {trail['factored_form']}")
    lines.append(f"Canonical Simplified Form: {trail['canonical_form']}")
    if trail.get("log_note") and trail.get("log_note") not in {trail.get("final_warning"), trail.get("summary_warning")}:
        lines.append(trail["log_note"])
    lines.append("")

    # VERIFICATION
    lines.append("VERIFICATION")
    lines.append(trail["verification"])
    lines.append("")

    # SUMMARY
    lines.append("SUMMARY")
    if trail.get("summary_warning"):
        lines.append(trail["summary_warning"])
    lines.append(trail["summary"])

    return "\n".join(lines)
