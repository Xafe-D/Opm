## 🧮 OPM: Symbolic Math Generator (v1.0 Final)

**OPM** is a desktop-based symbolic math engine built in Python for academic submission. It simplifies algebraic expressions step-by-step using a modular rule engine while showing a transparent solution trail and dedicated rule panels.

## 🚀 Quick Start

### Option 1: Run from source
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the application:
   ```bash
   python main.py
   ```

### Option 2: Standalone executable (Windows Only)
- If `OPM_Symbolic_Math_Generator.exe` is available, run it directly.
- The application is self-healing and will regenerate `history.json` if it is missing.

## ✅ What OPM Does

- Parses symbolic expressions and validates input syntax
- Applies algebraic rules in a controlled pipeline
- Generates a detailed step-by-step trail for learning
- Preserves history of calculations in `history.json`
- Exports solutions to `.txt` and `.pdf` (PDF export requires `reportlab`)

## ✨ Key Features

- **9 Dedicated Rule Panels** for:
  - Factorization
  - Special Products
  - Binomial Expansion
  - Combine Like Terms
  - Distributive Property
  - Exponent Rules
  - Multi-Term Distribution
  - Polynomial Simplification
  - Rational Simplification

- **Main Screen and Core Capabilities**
    OPM uses a strictly decoupled, modular architectural pipeline. Every algebraic expression is evaluated through 9 dedicated, rule-specific sub-engines to ensure isolated step-logging:

    1. Binomial Expansion Engine (`binomial_expansion.py`): Automatically detects and expands expressions raised to perfect powers, breaking down the calculation prior to further distribution layers.

    2. Combine Like Terms Module (`combine_like_terms.py`): Scans the expression tree to group and sum numerical coefficients sharing identical variable structures and exponents.

    3. Distributive Property Engine (`distributive_property.py`): Manages single-term scalar and variable distribution over parenthetical groupings.

    4. Exponent Rules Subsystem (`exponent_rules.py`): Simplifies products and quotients of literal bases by applying exponential laws (summing, subtracting, or multiplying powers).

    5. Factorization Module (`factorization.py`): Identifies quadratic patterns and pulls out greatest common factors (GCF) to produce structured product representations.

    6. Multi-Term Distribution Module (`multi_term_distribution.py`): Handles complex polynomial-by-polynomial multiplication pipelines (e.g., FOIL method and multi-bracket expansion layouts).

    7. Polynomial Simplification System (`polynomial_simplification.py`): Arranges terms into standard mathematical canonical form based on descending degrees of power.

    8. Rational Simplification Engine (`rational_simplification.py`): Evaluates fractions, identifying common algebraic factors between numerators and denominators for safe cancellation.

    9. Special Products Identifier (`special_products.py`): Detects classical algebraic identities—such as the Difference of Squares—to instantly skip tedious long-form steps when safe.

- **Full Visual Solution Trail** with step markers:
  - 🟢 GIVEN: Captures and prints the raw input expression.
  - 🟡 METHOD:Identifies the algebraic strategy and operations detected.
  - 🔵 STEPS: Displays the chronological, rule-by-rule transformations.
  - ✅ FINAL ANSWERS: Displays final answer in both factored and canonical form.
  - ✅ VERIFICATION: Shows if there's any residual and if it passed [OK] the verification or not.
  - ✳️ SUMMARY: Shows summary of the entire solution trail; the expression type, methods or operations detected, steps performed, execution time, timestamp, and SymPy version.

- **Retro-inspired GUI** with a sidebar history panel and rule navigation
- **Strict rule enforcement** and automatic syntax validation
- **Local history sidebar** for reviewing past calculations
- **Export capabilities** to `.txt` and `.pdf`

## 📦 Project Structure

```
Opm/
├── main.py
├── requirements.txt
├── symbolic_engine.py
├── test_engine.py
├── history.json
├── OPM_Symbolic_Math_Generator.exe
├── READMEfinal.md
├── READMEv1.md
├── TEST_PLANv1.md
└── symbolic_simplifier/
    ├── __init__.py
    ├── engine.py
    ├── main.py
    ├── parser.py
    ├── rules/
    │   ├── __init__.py
    │   ├── binomial_expansion.py
    │   ├── combine_like_terms.py
    │   ├── distributive_property.py
    │   ├── exponent_rules.py
    │   ├── factorization.py
    │   ├── multi_term_distribution.py
    │   ├── polynomial_simplification.py
    │   ├── rational_simplification.py
    │   └── special_products.py
    ├── ui/
    │   ├── __init__.py
    │   └── interface.py
    └── utils/
        ├── __init__.py
        ├── expression_formatter.py
        └── step_logger.py
```

## 🔧 Implementation Notes

- `main.py` launches the GUI application.
- `symbolic_engine.py` provides compatibility with older imports by re-exporting `symbolic_simplifier.process`.
- Core simplification logic is implemented in `symbolic_simplifier/engine.py`.
- The GUI and export features are implemented in `symbolic_simplifier/main.py`.

## 🧪 Dependencies

- Python 3.12+
- charset-normalizer
- customtkinter (UI Framework)
- darkdetect
- mpmath
- packaging
- pillow
- reportlab (PDF Generation Engine)
- sympy (Symbolic Math Core)

## 🧑‍🤝‍🧑 Team

- Miranda, Jessa Bien T.
- Oakes, Kenneth Gabren E.
- Pato, Mhira Shane O.
