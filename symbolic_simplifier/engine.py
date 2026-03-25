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
]

# Keep factorization as a reporting/optional derived transformation only.
FACTORIZATION_RULE = ("Factorization", apply_factor, "Factor polynomials")

RULE_MAP = {
    "Binomial Expansion": apply_binomial,
    "Distributive Property": apply_distributive,
    "Multi-Term Distribution": apply_multi_term,
    "Exponent Rules": apply_exponent,
    "Combine Like Terms": apply_combine,
    "Rational Expression Simplification": apply_rational,
    "Special Products": apply_special,
    "Factorization": apply_factor,
    "Polynomial Simplification": apply_polynomial,
}


def get_rule_pipeline(expr):
    """Return rule pipeline in correct order for the given expression."""
    num, den = expr.as_numer_denom()
    if den != 1:
        # For true rational expressions, prefer recognizing special products in
        # numerator before cancellation, so student-visible factoring appears.
        ordered = [
            ("Special Products", apply_special, "Factor special patterns"),
            ("Rational Expression Simplification", apply_rational, "Cancel common factors in fractions"),
        ]
        for item in RULE_PIPELINE:
            if item[0] not in {"Special Products", "Rational Expression Simplification"}:
                ordered.append(item)
        return ordered

    # For expressions that contain a multi-term product anywhere, prioritize multi-term distribution
    def contains_multi_term_product(e):
        from sympy import Mul, Add
        if isinstance(e, Mul):
            add_factors = [arg for arg in e.args if isinstance(arg, Add)]
            if len(add_factors) > 1:
                return True
        return any(contains_multi_term_product(arg) for arg in getattr(e, "args", []))

    if contains_multi_term_product(expr):
        ordered = [
            ("Binomial Expansion", apply_binomial, "Expand binomial powers"),
            ("Multi-Term Distribution", apply_multi_term, "Expand products of multiple terms"),
            ("Distributive Property", apply_distributive, "Expand multiplication over addition/subtraction"),
            ("Exponent Rules", apply_exponent, "Apply power rules"),
            ("Combine Like Terms", apply_combine, "Combine coefficients of identical variables"),
            ("Rational Expression Simplification", apply_rational, "Cancel common factors in fractions"),
            ("Special Products", apply_special, "Factor special patterns"),
        ]
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

    # If no transformation rules were actually applied and the final expression
    # can be factored (e.g., x^2 + 5x + 6), report Factorization as post-processing.
    def _needs_factorization(e):
        from sympy import factor

        if not e.is_polynomial():
            return False
        if isinstance(e, sympy.Mul):
            return False

        factored = factor(e)
        return factored.is_Mul and sympy.srepr(factored) != sympy.srepr(e)

    if not rule_steps_for_trail and _needs_factorization(expression):
        method_lines.append(f"{len(method_lines) - 1}. Post-processing: Factorization — Factor polynomials")

    # ---------------------------
    # METHOD output and RULE STEP DETAILS
    # ---------------------------
    trail["method"] = "\n".join(method_lines)
    trail["rule_steps"] = rule_steps_for_trail

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
    post_ops = []
    for line in method_lines[2:]:
        # each line is like "1. Name — description"; take the part before the dash
        if "—" in line:
            op = line.split("—")[0].strip()
        else:
            op = line.strip()
        # remove any leading numbering (e.g. "1.")
        op = op.lstrip('0123456789. ').strip()
        if op in {"Factorization", "Post-processing: Factorization"}:
            post_ops.append("Factorization")
        else:
            ops.append(op)

    ops_desc = ", ".join(ops) if ops else expr_type
    if post_ops:
        ops_desc = f"{ops_desc}; Post-processing: {', '.join(post_ops)}"

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

    def has_binomial_power(e):
        from sympy import Pow, Add
        if isinstance(e, Pow) and isinstance(e.base, Add) and e.exp.is_Integer and e.exp > 1:
            return True
        return any(has_binomial_power(arg) for arg in getattr(e, "args", []))

    def has_rational(e):
        from sympy import Pow
        num, den = e.as_numer_denom()
        if den != 1:
            return True
        return False

    def has_distributive(e):
        from sympy import Mul, Add, Pow
        if isinstance(e, Mul):
            add_factors = [arg for arg in e.args if isinstance(arg, Add)]
            if len(add_factors) > 1:
                # Prefer multi-term distribution for product of multiple additive factors
                return False
            if any(isinstance(arg, Add) for arg in e.args):
                return True
            if any(isinstance(arg, Pow) and isinstance(arg.base, Add) for arg in e.args):
                return True
        return any(has_distributive(arg) for arg in getattr(e, "args", []))

    def has_multi_term_distribution(e):
        from sympy import Mul, Add
        if isinstance(e, Mul):
            add_factors = [arg for arg in e.args if isinstance(arg, Add)]
            return len(add_factors) > 1
        return any(has_multi_term_distribution(arg) for arg in getattr(e, "args", []))

    def has_exponent(e):
        from sympy import Pow
        # detect exponent rules if any pow or power-of-power is present
        if isinstance(e, Pow) and isinstance(e.base, Pow):
            return True
        if e.has(Pow):
            return True
        return False

    def has_like_terms(e):
        from sympy import Add
        # If expression requires distribution or multi-term expansion,
        # combine-like-terms is conceptually part of the pipeline, even when no duplicates.
        if has_distributive(e) or has_multi_term_distribution(e) or has_binomial_power(e):
            return True

        if not isinstance(e, Add):
            return False

        if any(term.has(Add) for term in e.args):
            return False

        from collections import Counter
        monomials = []
        for term in e.args:
            coeff, factors = term.as_coeff_mul()
            monomials.append(tuple(sorted(str(f) for f in factors)))
        counts = Counter(monomials)
        return any(count > 1 for count in counts.values())

    def has_special_product(e):
        from .rules.special_products import _is_special_product
        return _is_special_product(e)

    def has_factorization(e):
        from sympy import factor
        try:
            if has_special_product(e):
                return False
            # Already factored form should not trigger factorization.
            if isinstance(e, sympy.Mul):
                return False
            # Factorization aims at expressing a polynomial as a product of simpler factors.
            if e.is_Add or e.is_poly:
                factored = factor(e)
                if factored.is_Mul and sympy.srepr(factored) != sympy.srepr(e):
                    return True
            return False
        except Exception:
            return False

    context_checks = {
        "Binomial Expansion": has_binomial_power,
        "Distributive Property": has_distributive,
        "Multi-Term Distribution": has_multi_term_distribution,
        "Exponent Rules": has_exponent,
        "Combine Like Terms": has_like_terms,
        "Rational Expression Simplification": has_rational,
        "Special Products": has_special_product,
        "Factorization": has_factorization,
    }

    pipeline = get_rule_pipeline(expr)
    seen_rules = set()
    for idx, (name, _, desc) in enumerate(pipeline, start=1):
        check = context_checks.get(name)
        if check and check(expr):
            method_lines.append(f"{idx}. {name} — {desc}")
            seen_rules.add(name)

    # Add Factorization hint in METHOD if not part of the RULE_PIPELINE,
    # because factorization is used for reporting and not as a destructive pipeline step.
    if "Factorization" not in seen_rules and context_checks["Factorization"](expr):
        method_lines.append(f"{len(method_lines) - 1}. Post-processing: Factorization — Factor polynomials")

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

        # If we only want to log rule even when not changed, we allow same/new and moved to `force_log`.
        if not force_log:
            if new_key in visited:
                return False
            if beautify_str(str(prev)) == beautify_str(str(new)):
                return False

        # update expression if changed
        if new != expr:
            expr = new
            visited.add(new_key)

        # Add step log when forced or when meaningful change occurred
        if force_log or beautify_str(str(prev)) != beautify_str(str(new)):
            steps.append({
                "rule": name,
                "description": description,
                "category": category,
                "before": beautify_str(str(prev)),
                "result": beautify_str(str(new)),
            })
            return new != prev

        return False

    rule_categories = {
        "Distributive Property": "Distribution",
        "Multi-Term Distribution": "Distribution",
        "Binomial Expansion": "Polynomial",
        "Exponent Rules": "Exponents",
        "Combine Like Terms": "Simplification",
        "Rational Expression Simplification": "Rational",
        "Special Products": "Factorization",
    }

    def _has_pending_expansion(e):
        from sympy import Add, Mul, Pow

        def has_binomial_expression(x):
            return isinstance(x, Pow) and isinstance(x.base, Add) and x.exp.is_Integer and x.exp > 1

        def has_distributive_pattern(x):
            if isinstance(x, Mul):
                add_factors = [arg for arg in x.args if isinstance(arg, Add)]
                if len(add_factors) > 1:
                    return True
                if any(isinstance(arg, Add) for arg in x.args):
                    return True
            return False

        if has_binomial_expression(e):
            return True
        if has_distributive_pattern(e):
            return True
        if isinstance(e, Add) or isinstance(e, Mul) or isinstance(e, Pow):
            return any(_has_pending_expansion(arg) for arg in getattr(e, 'args', []))
        return False

    iteration = 0
    while iteration < max_iterations:
        iteration += 1
        changed = False

        # Pre-analyze to avoid unnecessary expansion of factored special forms
        special_form = False
        try:
            from .rules.special_products import _is_special_product
            special_form = _is_special_product(expr)
        except Exception:
            special_form = False

        for name, func, desc in get_rule_pipeline(expr):
            category = rule_categories.get(name, "Rule")

            if special_form and name in {"Distributive Property", "Multi-Term Distribution"}:
                continue

            if try_rule(name, func, desc, category):
                changed = True

                # After expansion, try combine-like-terms:
                # - for Binomial/Distributive: only after no more pending expansion
                # - for Multi-Term: immediately (will handle subterms and flatten)
                if name in {"Binomial Expansion", "Distributive Property"}:
                    if not _has_pending_expansion(expr):
                        try_rule(
                            "Combine Like Terms",
                            apply_combine,
                            "Combine coefficients of identical variables",
                            "Simplification",
                        )
                elif name == "Multi-Term Distribution":
                    try_rule(
                        "Combine Like Terms",
                        apply_combine,
                        "Combine coefficients of identical variables",
                        "Simplification",
                    )

                # Re-run pipeline from first rule after each successful application
                break

        if not changed:
            return expr, steps, f"Completed after {iteration} iteration(s): exact symbolic form reached."

    return expr, steps, f"Stopped after reaching max iterations ({max_iterations})."


def process_by_rule(raw_expression: str, rule_name: str):
    """
    Process an expression using only a specific rule.
    Returns the result with a trail indicating if the rule was applied.
    """
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
        "method": f"METHOD: {rule_name} only",
        "steps": steps,
        "rule_steps": [],
        "factored_form": "",
        "canonical_form": "",
        "log_note": "",
        "verification": "",
        "summary": ""
    }

    # GIVEN
    log_step(f"Original expression: {raw_expression}")

    # VALIDATION
    valid, msg = validate_expression(raw_expression)
    if not valid:
        steps.append(f"Step {logical_step_counter + 1}: Validation failed: {msg}")
        trail["summary"] = "Computation terminated due to validation error."
        return {
            "status": "error",
            "error_message": msg,
            "final_answer": None,
            "final_answers": None,
            "formatted_trail": format_trail(trail),
        }

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

    # PARSING
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

    # Check if rule exists
    if rule_name not in RULE_MAP:
        error_msg = f"Unknown rule: {rule_name}"
        steps.append(f"ERROR: {error_msg}")
        trail["summary"] = error_msg
        return {
            "status": "error",
            "error_message": error_msg,
            "final_answer": None,
            "final_answers": None,
            "formatted_trail": format_trail(trail),
        }

    # Apply the specific rule
    rule_func = RULE_MAP[rule_name]
    
    # Get description from RULE_PIPELINE or FACTORIZATION_RULE
    rule_desc = ""
    for name, func, desc in RULE_PIPELINE:
        if name == rule_name:
            rule_desc = desc
            break
    if not rule_desc and rule_name == "Factorization":
        rule_desc = "Factor polynomials"
    if not rule_desc:
        rule_desc = f"Apply {rule_name.lower()}"

    original_expr = expression
    try:
        new_expr = rule_func(expression)
    except Exception as e:
        new_expr = expression
        log_step(f"Rule application failed: {str(e)}")

    if beautify_str(str(original_expr)) == beautify_str(str(new_expr)):
        # No change
        log_step(
            f"Applied {rule_name}",
            [
                f"- Attempted to apply: {rule_desc}",
                "- No applicable pattern detected",
                f"- Result: {beautify_str(str(new_expr))} (No changes made)"
            ]
        )
        trail["log_note"] = f"No {rule_name.lower()} pattern detected."
        trail["summary"] = f"FINAL ANSWER: {beautify_str(str(new_expr))}"
    else:
        # Changed
        log_step(
            f"Applied {rule_name}",
            [
                f"- Applied: {rule_desc}",
                f"- Before: {beautify_str(str(original_expr))}",
                f"- After: {beautify_str(str(new_expr))}"
            ]
        )
        trail["rule_steps"] = [{
            "rule": rule_name,
            "description": rule_desc,
            "before": beautify_str(str(original_expr)),
            "result": beautify_str(str(new_expr)),
        }]
        trail["log_note"] = f"Successfully applied {rule_name.lower()}."
        trail["summary"] = f"FINAL ANSWER: {beautify_str(str(new_expr))}"

    end_time = time.time()
    processing_time = end_time - start_time

    return {
        "status": "success",
        "final_answer": beautify_str(str(new_expr)),
        "final_answers": [beautify_str(str(new_expr))],
        "processing_time": processing_time,
        "formatted_trail": format_trail(trail),
    }
