"""
Engine Module

Core symbolic simplification engine that orchestrates the simplification process.
Manages the pipeline: validation -> parsing -> rule application -> verification.
"""

import time
from datetime import datetime
import sympy
from sympy import simplify, factor
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)

from .parser import validate_expression, parse_expression
from .utils.expression_formatter import beautify_str, format_trail

# rule modules imported once so detect + apply share identical pipeline order
from .rules.binomial_expansion import apply_rule as apply_binomial
from .rules.distributive_property import apply_rule as apply_distributive
from .rules.multi_term_distribution import apply_rule as apply_multi_term
from .rules.exponent_rules import apply_rule as apply_exponent
from .rules.combine_like_terms import apply_rule as apply_combine
from .rules.rational_simplification import apply_rule as apply_rational
from .rules.special_products import apply_rule as apply_special
from .rules.factorization import apply_rule as apply_factor
from .rules.polynomial_simplification import apply_rule as apply_polynomial

RULE_PIPELINE = [
    ("Binomial Expansion", apply_binomial, "Expand binomial powers"),
    ("Distributive Property", apply_distributive, "Expand multiplication over addition/subtraction"),
    ("Multi-Term Distribution", apply_multi_term, "Expand products of multiple terms"),
    ("Exponent Rules", apply_exponent, "Apply power rules"),
    ("Combine Like Terms", apply_combine, "Combine coefficients of identical variables"),
    ("Rational Expression Simplification", apply_rational, "Cancel common factors in fractions"),
    ("Special Products", apply_special, "Factor special patterns"),
    ("Factorization", apply_factor, "Factor polynomials"),
]


def get_rule_pipeline(expr):
    """Return rule pipeline in correct order for the given expression."""
    num, den = expr.as_numer_denom()
    if den != 1:
        # For true rational expressions (nontrivial denominator), prefer special products and rational simplification
        # and factorization before expansions to avoid unnecessary numerator expansion.
        ordered = [
            ("Special Products", apply_special, "Factor special patterns"),
            ("Rational Expression Simplification", apply_rational, "Cancel common factors in fractions"),
            ("Factorization", apply_factor, "Factor polynomials"),
        ]
        # add remaining rules from base pipeline preserving order and avoiding duplicates
        for item in RULE_PIPELINE:
            if item[0] not in {"Special Products", "Rational Expression Simplification", "Factorization"}:
                ordered.append(item)
        return ordered

    return RULE_PIPELINE



def process(raw_expression: str, max_iterations: int = 20):
    start_time = time.time()
    steps = []
    logical_step_counter = 0

    def log_step(description, sublines=None):
        nonlocal logical_step_counter
        logical_step_counter += 1
        steps.append(f"Step {logical_step_counter}: {description}")
        if sublines:
            for sub in sublines:
                steps.append(f"    {sub}")

    trail = {
        "given": raw_expression,
        "method": "",
        "steps": steps,
        "rule_steps": [],
        "factored_form": "",
        "canonical_form": "",
        "log_note": "",
        "verification": "",
        "summary": ""
    }

    # ---------------------------
    # GIVEN
    # ---------------------------
    log_step(f"Original expression: {raw_expression}")

    # ---------------------------
    # VALIDATION
    # ---------------------------
    valid, msg = validate_expression(raw_expression)
    if valid:
        detected_vars = "N/A"
        try:
            expr_str = raw_expression.replace("^", "**")
            transformations = standard_transformations + (
                implicit_multiplication_application,
            )
            sym_expr = parse_expr(
                expr_str,
                transformations=transformations,
                evaluate=False,
            )
            vars_detected = sorted([str(s) for s in sym_expr.free_symbols])
            detected_vars = ", ".join(vars_detected)
        except:
            pass
        log_step(
            "Validation",
            [
                "- Checked expression syntax: valid",
                f"- Detected variable(s): {detected_vars}",
            ],
        )
    else:
        steps.append(f"Step {logical_step_counter + 1}: Validation failed: {msg}")
        trail["summary"] = "Computation terminated due to validation error."
        return {
            "status": "error",
            "error_message": msg,
            "final_answer": None,
            "final_answers": None,
            "formatted_trail": format_trail(trail),
        }

    # ---------------------------
    # PARSING
    # ---------------------------
    try:
        expression = parse_expression(raw_expression)
        log_step(
            "Parsing",
            [
                f"- Converted input into SymPy symbolic object: {beautify_str(str(expression))}"
            ],
        )
    except Exception as e:
        steps.append(f"ERROR: Could not parse expression. {str(e)}")
        trail["summary"] = "Computation terminated due to parsing error."
        return {
            "status": "error",
            "error_message": f"Parsing error: {str(e)}",
            "final_answer": None,
            "final_answers": None,
            "formatted_trail": format_trail(trail),
        }

    # ---------------------------
    # EXPRESSION TYPE
    # ---------------------------
    expr_type = detect_expression_type(expression)
    log_step(
        "Simplification preparation",
        [
            f"- Expression type determined: {expr_type}",
            "- Checked for constants, coefficients, and powers",
        ],
    )

    # ---------------------------
    # DETECT METHOD ACCURATELY (Prediction Only)
    # ---------------------------
    detected_method_lines = detect_method(expression)

    # --------------------------- 
    # APPLY ALGEBRA RULES
    # ---------------------------
    expression, rule_steps_for_trail, completion_reason = apply_algebra_rules(
        expression,
        raw_input=raw_expression,
        max_iterations=max_iterations,
    )

    # record completion or stopping criteria clearly in the trail
    trail["log_note"] = completion_reason

    # ---------------------------
    # METHOD derived from executed steps to keep METHOD and STEPS in sync
    # ---------------------------
    method_lines = [
        "Rule-based symbolic simplification using algebraic transformation rules.",
        "Detected operations:",
    ]

    if rule_steps_for_trail:
        for idx, rstep in enumerate(rule_steps_for_trail, start=1):
            method_lines.append(f"{idx}. {rstep['rule']} — {rstep.get('description', '')}")
    else:
        method_lines.append("No transformation rules were required; the expression was already simplified.")

    trail["method"] = "\n".join(method_lines)
    trail["rule_steps"] = rule_steps_for_trail
    # RULE STEP DETAILS
    # ---------------------------
    for rstep in trail.get("rule_steps", []):
        sublines = [f"- {rstep['description']}"]
        before = rstep.get("before", "")
        after = rstep.get("result", "")
        rule = rstep["rule"]
        if before != after:
            sublines.append(f"a) Before: {before}")
            sublines.append(f"b) Apply rule: {rule}")
            sublines.append(f"c) Result: {after}")
        else:
            sublines.append("- No change; already simplified")
        log_step(rule, sublines)

    # ---------------------------
    # GENERATE FACTORED REPRESENTATION
    # ---------------------------
    factored = factor(expression)
    raw_fact = str(factored if factored != expression else expression)
    trail["factored_form"] = beautify_str(raw_fact)
    sublines = ["- Checked for common factors"]
    if factored == expression:
        rational_step_applied = any(rstep.get("rule") == "Rational Expression Simplification" for rstep in trail.get("rule_steps", []))
        try:
            original_expr_sym = parse_expression(raw_expression)
            num, den = original_expr_sym.as_numer_denom()
            if den != 1 and original_expr_sym != expression:
                rational_step_applied = True
        except Exception:
            pass

        if rational_step_applied:
            try:
                original_expr_sym = parse_expression(raw_expression)
                num, den = original_expr_sym.as_numer_denom()
                fact_num = factor(num)
                fact_den = factor(den)
                if fact_num != num:
                    sublines.append(f"- Numerator factored: {beautify_str(str(fact_num))}")
                if fact_den != den:
                    sublines.append(f"- Denominator factored: {beautify_str(str(fact_den))}")
                num_factors = list(fact_num.args) if isinstance(fact_num, sympy.Mul) else [fact_num]
                den_factors = list(fact_den.args) if isinstance(fact_den, sympy.Mul) else [fact_den]
                common_factors = [f for f in num_factors if f in den_factors]
                if common_factors:
                    common_list = ", ".join(beautify_str(str(f)) for f in common_factors)
                    sublines.append(f"- Common factor(s) cancelled: {common_list}")
                else:
                    sublines.append("- Common factor(s) already cancelled by prior step")
            except Exception:
                sublines.append(f"- No factors to extract; result unchanged: {trail['factored_form']}")
        else:
            sublines.append(f"- No factors to extract; result unchanged: {trail['factored_form']}")
    else:
        sublines.append(f"- Factored form: {trail['factored_form']}")
    log_step("Generate Factored Representation", sublines)
    # ---------------------------
    # CANONICAL SIMPLIFICATION
    # ---------------------------
    # For polynomials, canonical representation should be expanded.
    if expression.is_polynomial():
        simplified = sympy.expand(expression)
        canon_note = "- Expanded polynomial to canonical form"
    else:
        simplified = simplify(expression)
        canon_note = "- Ensured standard form (sorted terms, minimal coefficients)"

    raw_canon = str(simplified)
    trail["canonical_form"] = beautify_str(raw_canon)
    log_step(
        "Canonical simplification",
        [
            canon_note,
            f"- Result: {trail['canonical_form']}",
        ],
    )

    # ---------------------------
    # VERIFICATION
    # ---------------------------
    try:
        residual_factored = simplify(expression - factored)
        residual_canonical = simplify(expression - simplified)
        status = "Passed" if residual_factored == 0 and residual_canonical == 0 else "Failed"
        log_step(
            "Verification",
            [
                "- Compared original and simplified expressions symbolically",
                f"- Result: {beautify_str(str(expression))} == {beautify_str(str(simplified))} → {status}",
            ],
        )
        trail["verification"] = (
            f"Residual (Factored - Original): {residual_factored}\n"
            f"Residual (Canonical - Original): {residual_canonical}\n"
            f"Status: {status}"
        )
    except Exception as e:
        log_step("Verification Error", [f"- {str(e)}"])
        trail["verification"] = f"Verification Error: {str(e)}"

    # ---------------------------
    # COMPLETION STATE
    # ---------------------------
    log_step("Completion state", [f"- {completion_reason}"])

    # ---------------------------
    # FINAL OUTPUT
    # ---------------------------
    log_step("Final Output", [f"- Simplified expression: {trail['canonical_form']}"])

    # ---------------------------
    # SUMMARY
    # ---------------------------
    elapsed = time.time() - start_time
    # operations: if the method detector added lines after the header, list their names
    ops = []
    for line in method_lines[2:]:
        # each line is like "1. Name — description"; take the part before the dash
        if "—" in line:
            op = line.split("—")[0].strip()
        else:
            op = line.strip()
        # remove any leading numbering (e.g. "1.")
        op = op.lstrip('0123456789. ').strip()
        ops.append(op)
    ops_desc = ", ".join(ops) if ops else expr_type
    trail["summary"] = (
        f"Expression type: {expr_type}\n"
        f"Operations detected: {ops_desc}\n"
        f"Steps performed: {logical_step_counter}\n"
        f"Execution time: {elapsed:.4f} sec\n"
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"SymPy version: {sympy.__version__}"
    )

    return {
        "status": "success",
        "final_answer": beautify_str(raw_canon),
        "final_answers": {
            "factored_form": trail["factored_form"],
            "canonical_form": trail["canonical_form"],
            "log_note": trail.get("log_note", ""),
        },
        "formatted_trail": format_trail(trail),
    }


def detect_expression_type(expr):
    if expr.free_symbols == set():
        return "Constant expression"
    if expr.has(sympy.sin, sympy.cos, sympy.tan):
        return "Trigonometric"
    elif expr.has(sympy.log):
        return "Logarithmic"
    elif expr.has(sympy.exp):
        return "Exponential"
    elif expr.is_polynomial():
        return "Polynomial"
    elif expr.is_rational_function():
        return "Rational"
    else:
        return "Algebraic"


# ---------------------------
# ACCURATE METHOD DETECTION
# ---------------------------
def detect_method(expr):
    """Detect applicable rules without generating rule step details."""
    method_lines = [
        "Rule-based symbolic simplification using algebraic transformation rules.",
        "Detected operations:",
    ]

    original_expr = expr

    def has_binomial_power(e):
        from sympy import Pow, Add
        if isinstance(e, Pow) and isinstance(e.base, Add) and e.exp.is_Integer and e.exp > 1:
            return True
        return any(has_binomial_power(arg) for arg in getattr(e, "args", []))

    def has_fraction(e):
        from sympy import Rational, Pow, Mul
        if isinstance(e, Rational):
            return True
        if isinstance(e, Pow) and e.exp.is_Number and e.exp < 0:
            return True
        if isinstance(e, Mul):
            return any(isinstance(arg, Pow) and arg.exp.is_Number and arg.exp < 0 for arg in e.args)
        return False

    def has_multi_term_distribution(e):
        if has_fraction(e):
            return False
        from sympy import Mul, Add
        if isinstance(e, Mul):
            add_factors = [arg for arg in e.args if isinstance(arg, Add)]
            return len(add_factors) > 1
        return any(has_multi_term_distribution(arg) for arg in getattr(e, "args", []))

    def has_distributive(e):
        from sympy import Mul, Add, Pow
        if isinstance(e, Mul):
            add_factors = [arg for arg in e.args if isinstance(arg, Add)]
            if len(add_factors) == 1:
                other_factors = [arg for arg in e.args if arg not in add_factors]
                if any(isinstance(arg, Pow) and arg.exp.is_number and arg.exp < 0 for arg in other_factors):
                    return False
                return True
            if len(add_factors) > 1:
                other_factors = [arg for arg in e.args if arg not in add_factors]
                if any(arg.is_Number for arg in other_factors):
                    return True
            pow_add = [arg for arg in e.args if isinstance(arg, Pow) and isinstance(arg.base, Add)]
            if pow_add:
                if any(arg.exp.is_number and arg.exp < 0 for arg in pow_add):
                    return False
                return True
        return any(has_distributive(arg) for arg in getattr(e, "args", []))

    def has_exponent(e):
        from sympy import Pow, Mul
        if not e.has(Pow):
            return False

        if isinstance(e, Mul):
            powers = [arg for arg in e.args if isinstance(arg, Pow)]
            if len(powers) >= 2:
                return True

        if isinstance(e, Pow) and isinstance(e.base, Pow):
            return True

        # allow x^a/x^b with negative exponents in Mul form
        if isinstance(e, Mul):
            pow_args = [arg for arg in e.args if isinstance(arg, Pow)]
            if len(pow_args) >= 2:
                return True

        return any(has_exponent(arg) for arg in getattr(e, "args", []))

    def has_like_terms(e):
        from sympy import Add, Mul, Pow
        if isinstance(original_expr, Mul):
            if any(isinstance(arg, Pow) and arg.exp.is_number and arg.exp < 0 for arg in original_expr.args):
                return False
            add_factors = [arg for arg in original_expr.args if isinstance(arg, Add)]
            if len(add_factors) > 1:
                return True

        if isinstance(original_expr, Add) and len(original_expr.args) > 1:
            has_binomial_pow = any(isinstance(arg, Pow) and isinstance(arg.base, Add) for arg in original_expr.args)
            has_mul_with_add = any(isinstance(arg, Mul) and any(isinstance(a, Add) for a in arg.args) for arg in original_expr.args)
            if has_binomial_pow and has_mul_with_add:
                return True

        if isinstance(e, Add):
            monomials = []
            for term in e.args:
                coeff, vars_ = term.as_coeff_mul()
                key = tuple(sorted(vars_, key=str))
                monomials.append(key)
            from collections import Counter
            monomial_counts = Counter(monomials)
            return any(count > 1 for count in monomial_counts.values())

        return any(has_like_terms(arg) for arg in getattr(e, "args", []))

    def has_special_product(e):
        from .rules.special_products import _is_special_product
        return _is_special_product(e)


    def has_factorization(e):
        from sympy import factor, Mul, Add, Pow
        if has_special_product(e):
            return False
        if isinstance(original_expr, Add) and len(original_expr.args) > 1:
            has_binomial_pow = any(isinstance(arg, Pow) and isinstance(arg.base, Add) for arg in original_expr.args)
            has_mul_with_add = any(isinstance(arg, Mul) and any(isinstance(a, Add) for a in arg.args) for arg in original_expr.args)
            if has_binomial_pow and has_mul_with_add:
                return False
        if isinstance(original_expr, Mul) and any(isinstance(arg, Add) for arg in original_expr.args):
            return False
        try:
            factored = factor(e)
        except Exception:
            return False
        if factored == e:
            return False
        if isinstance(factored, Mul):
            non_constant_factors = [f for f in factored.args if not f.is_Number]
            return len(non_constant_factors) >= 2
        return False

    def has_polynomial(e):
        if not e.is_polynomial():
            return False
        from sympy import Add
        if isinstance(e, Add):
            degrees = []
            for term in e.args:
                if term.is_polynomial():
                    poly = term.as_poly()
                    deg = sum(poly.degree_list()) if poly is not None else 0
                else:
                    deg = 0
                degrees.append(deg)
            return degrees != sorted(degrees, reverse=True)
        return False

    context_checks = {
        "Binomial Expansion": has_binomial_power,
        "Distributive Property": has_distributive,
        "Multi-Term Distribution": has_multi_term_distribution,
        "Exponent Rules": has_exponent,
        "Combine Like Terms": has_like_terms,
        "Rational Expression Simplification": has_fraction,
        "Special Products": has_special_product,
        "Factorization": has_factorization,
    }

    pipeline = get_rule_pipeline(expr)
    for idx, (name, _, desc) in enumerate(pipeline, start=1):
        check = context_checks.get(name)
        if check and check(expr):
            method_lines.append(f"{idx}. {name} — {desc}")

    if len(method_lines) == 2:
        method_lines.append("No transformation rules were required; the expression was already simplified.")

    return method_lines



def apply_algebra_rules(expr, raw_input=None, max_iterations=20):
    steps = []
    import sympy as _sym
    visited = {_sym.srepr(expr)}

    if max_iterations <= 0:
        return expr, steps, f"Stopped before simplification: max_iterations set to {max_iterations}."

    def try_rule(name, func, description, category, *args, force_log=False):
        nonlocal expr
        prev = expr
        try:
            new = func(expr, *args)
        except Exception:
            new = expr
        new_key = _sym.srepr(new)

        if force_log:
            if new != expr:
                expr = new
                visited.add(_sym.srepr(expr))
            steps.append({
                "rule": name,
                "description": description,
                "category": category,
                "before": beautify_str(str(prev)),
                "result": beautify_str(str(new)),
            })
            return

        if new_key in visited:
            return

        # Avoid logging purely syntactic noise (e.g., 1*16 -> 16) when
        # nothing meaningful changed.
        if beautify_str(str(prev)) == beautify_str(str(new)):
            return

        expr = new
        visited.add(_sym.srepr(expr))
        steps.append({
            "rule": name,
            "description": description,
            "category": category,
            "before": beautify_str(str(prev)),
            "result": beautify_str(str(expr)),
        })


    def term_count(ex):
        if ex is None:
            return 0
        if hasattr(ex, 'is_Add') and ex.is_Add:
            return len(ex.args)
        return 1

    def run_single_pass(current_expr):
        nonlocal steps, expr
        pipeline = get_rule_pipeline(current_expr)
        binomial_candidate = False
        multi_term_applied = False

        for idx, (name, func, desc) in enumerate(pipeline, start=1):
            if name == "Factorization" and multi_term_applied:
                # For educational trace, do not factor expanded polynomial that was
                # recently produced by multi-term distribution in the same chain.
                continue
            category = "Rule"
            if name == "Distributive Property" or name == "Multi-Term Distribution":
                category = "Distribution"
            elif name in ["Binomial Expansion", "Polynomial Simplification"]:
                category = "Polynomial"
            elif name == "Special Products" or name == "Factorization":
                category = "Factorization"
            elif name == "Exponent Rules":
                category = "Exponents"
            elif name == "Rational Expression Simplification":
                category = "Rational"
            elif name == "Combine Like Terms":
                category = "Simplification"

            # detect special binomial+distribution shape: Number * (Add)**n
            if name == "Binomial Expansion":
                if isinstance(current_expr, sympy.Mul):
                    coeffs = [arg for arg in current_expr.args if arg.is_Number]
                    pow_add = [arg for arg in current_expr.args if isinstance(arg, sympy.Pow) and isinstance(arg.base, sympy.Add) and arg.exp.is_integer and arg.exp > 1]
                    if coeffs and pow_add:
                        binomial_candidate = True

            pre_terms = term_count(current_expr)
            old_expr = current_expr
            # We'll temporarily assign expr to current_expr and restore after try_rule
            backup_expr = expr
            expr = current_expr
            try_rule(name, func, desc, category)
            current_expr = expr
            expr = backup_expr

            # track whether multi-term distribution actually changed the expression
            if name == "Multi-Term Distribution" and current_expr != old_expr:
                multi_term_applied = True

            # for binomial candidate, ensure distributive is captured for educational trace
            if name == "Binomial Expansion" and binomial_candidate:
                distributed = apply_distributive(current_expr)
                if distributed != current_expr:
                    # adjust expression in outer scope
                    backup_expr = expr
                    expr = current_expr
                    try_rule(
                        "Distributive Property",
                        apply_distributive,
                        "Expand multiplication over addition/subtraction",
                        "Distribution",
                    )
                    current_expr = expr
                    expr = backup_expr
                else:
                    # Log educational step even if expression did not change
                    steps.append({
                        "rule": "Distributive Property",
                        "description": "Expand multiplication over addition/subtraction",
                        "category": "Distribution",
                        "before": beautify_str(str(current_expr)),
                        "result": beautify_str(str(current_expr)),
                    })

            # after multi-term distribution, force combine-like-terms step for educational tracing
            if name == "Multi-Term Distribution":
                post_terms = term_count(current_expr)
                # only force combine when the preceding rule actually changed the expression
                # and the result is a sum or has fewer terms (indicates expansion)
                if current_expr != old_expr and (current_expr.is_Add or post_terms < pre_terms):
                    backup_expr = expr
                    expr = current_expr
                    try_rule(
                        "Combine Like Terms",
                        apply_combine,
                        "Combine coefficients of identical variables",
                        "Simplification",
                        force_log=True,
                    )
                    current_expr = expr
                    expr = backup_expr

        return current_expr

    # Iteratively apply rules until fixed point or max_iterations reached
    for iteration in range(1, max_iterations + 1):
        old_expr = expr
        expr = run_single_pass(expr)
        if expr == old_expr:
            return expr, steps, f"Completed after {iteration} iteration(s): exact symbolic form reached."

    return expr, steps, f"Stopped after reaching max iterations ({max_iterations})."
