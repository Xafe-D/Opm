"""
Engine Module

Core symbolic simplification engine that orchestrates the simplification process.
Manages the pipeline: validation -> parsing -> rule application -> verification.

Functions:
    - process(): Main entry point for expression simplification
    - detect_expression_type(): Identify expression category
    - apply_algebra_rules(): Apply sequence of algebraic rules
"""

import re
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


def process(raw_expression: str):
    """Main entry point for symbolic expression simplification.
    
    Orchestrates the complete simplification pipeline:
    1. Validation of input
    2. Parsing to SymPy expression
    3. Expression type detection
    4. Application of algebraic rules
    5. Verification of results
    
    Args:
        raw_expression: String containing the mathematical expression
        
    Returns:
        Dictionary with keys:
            - status: "success" or "error"
            - final_answer: Simplified form as string
            - final_answers: Dict with factored_form, canonical_form
            - formatted_trail: Complete step-by-step output
            - error_message: (if status is "error")
    """
    start_time = time.time()
    steps = []
    step_counter = 1  # dynamic step numbering

    trail = {
        "given": raw_expression,
        "method": "Rule-based simplification engine applying algebraic properties via SymPy",
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
    steps.append(f"Step {step_counter}: Original expression: {raw_expression}")
    step_counter += 1

    # ---------------------------
    # VALIDATION
    # ---------------------------
    valid, msg = validate_expression(raw_expression)
    if valid:
        steps.append(f"Step {step_counter}: Validation passed")
        step_counter += 1
    else:
        steps.append(f"Step {step_counter}: Validation failed: {msg}")
        trail["summary"] = "Computation terminated due to validation error."
        return {
            "status": "error",
            "error_message": msg,
            "final_answer": None,
            "final_answers": None,
            "formatted_trail": format_trail(trail)
        }

    # ---------------------------
    # PARSING
    # ---------------------------
    try:
        expression = parse_expression(raw_expression)
        # record the structure as parsed (don't simplify yet)
        steps.append(f"Step {step_counter}: Parsed expression: {beautify_str(str(expression))}")
        step_counter += 1
    except Exception as e:
        steps.append(f"ERROR: Could not parse expression. {str(e)}")
        trail["summary"] = "Computation terminated due to parsing error."
        return {
            "status": "error",
            "error_message": f"Parsing error: {str(e)}",
            "final_answer": None,
            "final_answers": None,
            "formatted_trail": format_trail(trail)
        }

    # ---------------------------
    # METHOD
    # ---------------------------
    steps.append(f"Step {step_counter}: Applying simplification methods...")
    step_counter += 1

    # ---------------------------
    # DETECT TYPE
    # ---------------------------
    expr_type = detect_expression_type(expression)
    steps.append(f"Step {step_counter}: Recognized expression type: {expr_type}")
    step_counter += 1

    # ---------------------------
    # SIMPLIFICATIONS / DETAILED REASONING
    # ---------------------------
    # use rule engine to apply algebraic properties one at a time
    expression, rule_steps = apply_algebra_rules(expression, raw_input=raw_expression)

    # after rules have been applied, recompute derived forms
    factored = factor(expression)
    simplified = simplify(expression)

    # Store rule steps in trail for detailed reporting
    trail["rule_steps"] = rule_steps

    # Process and log each applied rule step
    for rstep in rule_steps:
        steps.append(f"Step {step_counter}: [{rstep['category']}] {rstep['rule']}")
        if 'before' in rstep:
            steps.append(f"         Before: {rstep['before']}")
        steps.append(f"         => {rstep['description']}")
        steps.append(f"         => Result: {rstep['result']}")
        step_counter += 1

    # ---------------------------
    # FINAL ANSWERS
    # ---------------------------
    raw_fact = str(factored if factored != expression else expression)
    trail["factored_form"] = beautify_str(raw_fact)
    steps.append(f"Step {step_counter}: Factored form: {trail['factored_form']}")
    step_counter += 1

    raw_canon = str(simplified)
    trail["canonical_form"] = beautify_str(raw_canon)
    steps.append(f"Step {step_counter}: Canonical simplified form: {trail['canonical_form']}")
    step_counter += 1

    # ---------------------------
    # VERIFICATION
    # ---------------------------
    try:
        residual_factored = simplify(expression - factored)
        residual_canonical = simplify(expression - simplified)
        status = "Passed" if residual_factored == 0 and residual_canonical == 0 else "Failed"
        trail["verification"] = (
            f"Residual (Factored - Original): {residual_factored}\n"
            f"Residual (Canonical - Original): {residual_canonical}\n"
            f"Status: {status}"
        )
        steps.append(f"Step {step_counter}: Verification {status}")
        step_counter += 1
    except Exception as e:
        trail["verification"] = f"Verification Error: {str(e)}"
        steps.append(f"Step {step_counter}: {trail['verification']}")
        step_counter += 1

    # ---------------------------
    # SUMMARY
    # ---------------------------
    elapsed = time.time() - start_time
    trail["summary"] = (
        f"Expression type: {expr_type}\n"
        f"Operations detected: {expr_type}\n"
        f"Steps performed: {len(steps)}\n"
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
            "log_note": trail.get("log_note", "")
        },
        "formatted_trail": format_trail(trail)
    }


def detect_expression_type(expr) -> str:
    """Detect the mathematical type of the expression.
    
    Args:
        expr: SymPy expression object
        
    Returns:
        String describing expression type:
        - "Trigonometric"
        - "Logarithmic"
        - "Exponential"
        - "Polynomial"
        - "Rational"
        - "Algebraic"
    """
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


def apply_algebra_rules(expr, raw_input: str = None):
    """Apply a sequence of algebraic rules to simplify the expression.
    
    Applies rules in order with detailed step tracking:
    1. Distributive Property
    2. Rational Expression Simplification
    3. Combine Like Terms
    4. Multi-Term Distribution
    5. Exponent Rules
    6. Binomial Expansion
    7. Special Products
    8. Polynomial Simplification
    
    Args:
        expr: SymPy expression to simplify
        raw_input: Optional original string for pattern detection
        
    Returns:
        Tuple of (final_expression, applied_steps_list) where applied_steps_list
        is a list of dictionaries describing only the rules that actually
        modified the expression.  Skipped/inapplicable rules are omitted.
    """
    from .rules.distributive_property import apply_rule as apply_distributive
    from .rules.rational_simplification import apply_rule as apply_rational
    from .rules.combine_like_terms import apply_rule as apply_combine
    from .rules.multi_term_distribution import apply_rule as apply_multi_term
    from .rules.exponent_rules import apply_rule as apply_exponent
    from .rules.binomial_expansion import apply_rule as apply_binomial
    from .rules.special_products import apply_rule as apply_special
    from .rules.polynomial_simplification import apply_rule as apply_polynomial
    
    steps = []
    from .utils.expression_formatter import beautify_str

    def try_rule(name, func, description, category, *args, always_log=False):
        """Try applying a rule and optionally log its action.
        
        The normal behaviour is to record only rules that change the
        expression.  However certain rules (e.g. combining like terms) are
        helpful to log even when the expression is already in simplest form;
        in that case ``always_log`` may be set to ``True``.
        
        Entries now include a ``before`` field showing the expression state
        immediately prior to the rule, giving the user a clearer picture of
        the transformation.
        
        Args:
            name: Name of the rule
            func: Function that applies the rule
            description: Description of what the rule does
            category: Category of the rule (e.g., "Polynomial", "Rational")
            *args: Arguments to pass to the function
            always_log: If True, create an entry even if the expression was
                        unchanged.
        """
        nonlocal expr
        prev = expr
        try:
            new = func(expr, *args)
        except Exception:
            new = expr
        
        if new != expr or always_log:
            expr = new
            result_str = beautify_str(str(expr))
            steps.append({
                'rule': name,
                'description': description,
                'category': category,
                'before': beautify_str(str(prev)),
                'result': result_str,
                'expression': expr
            })

    # Define detailed rule descriptions
    # move combine-like-terms before distribution to make its action
    # explicit for simple expressions like 10x-9x
    rules = [
        (
            "Combine Like Terms",
            apply_combine,
            "Combine coefficients of identical variables",
            "Simplification",
            [],
            True,    # always_log: we want to record it even if nothing changes
        ),
        (
            "Distributive Property",
            apply_distributive,
            "Expand multiplication over addition/subtraction",
            "Distribution",
            [raw_input],
            False,
        ),
        (
            "Rational Expression Simplification",
            apply_rational,
            "Factor numerator and denominator, then cancel common factors",
            "Rational",
            [steps],
            False,
        ),
        (
            "Multi-Term Distribution",
            apply_multi_term,
            "Expand products of multiple terms",
            "Distribution",
            [],
            False,
        ),
        (
            "Exponent Rules",
            apply_exponent,
            "Apply power rules",
            "Exponents",
            [],
            False,
        ),
        (
            "Binomial Expansion",
            apply_binomial,
            "Expand binomial powers",
            "Polynomial",
            [],
            False,
        ),
        (
            "Special Products",
            apply_special,
            "Factor special patterns",
            "Factorization",
            [],
            False,
        ),
        (
            "Polynomial Simplification",
            apply_polynomial,
            "Arrange in standard polynomial form",
            "Polynomial",
            [],
            False,
        ),
    ]

    # Apply each rule with detailed logging (failed/skipped rules
    # produce no entry in ``steps`` because they are not interesting).
    for rule_name, rule_func, rule_desc, rule_category, rule_args, always in rules:
        try_rule(rule_name, rule_func, rule_desc, rule_category, *rule_args, always_log=always)

    # ``steps`` now contains only applied-rule records
    return expr, steps
