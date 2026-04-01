## 🧮 OPM: Symbolic Math Generator (v1 Midterm)
OPM is a desktop-based symbolic math engine built with Python. It provides step-by-step algebraic simplification with a focus on pedagogical transparency through its unique Solution Trail and Strict Rule Enforcement panels.

## 🚀 Quick Start
**Option 1: Standalone Executable (Windows Only)**
Navigate to the /OPM_Symbolic_Math_Generator.exe folder.

Double-click OPM_Symbolic_Math_Generator.exe.

Note: The application is "Self-Healing." If history.json is missing, it will automatically generate a fresh database upon launch.

**Option 2: Developer Mode (Source Code)**
Install Dependencies:
Bash
`pip install -r requirements.txt`

List of Dependencies:
- `Python 3.12+`
- `charset-normalizer`
- `customtkinter`
- `darkdetect`
- `mpmath`
- `packaging`
- `pillow`
- `reportlab`
- `sympy`

Run Application:
Bash
`python main.py`

## ✨ Key Features
- Main Screen as General Solver: Simplify symbolic expressions using a modular rule engine, and-

- 9 Dedicated Rule Panels: Specialized tools for Factorization, Special Products, Binomial Expansion, Combine Like Terms, Distributive Property, Exponent Rules, Multi-Term Distribution, Polynomial Simplification, and Rational Simplification.

- Full Visual Solution Trail: 🟢 GIVEN, 🟡 METHOD, 🔵 STEPS, ✅ FINAL ANSWERS, ✅ VERIFICATION, and ✳️ SUMMARY to explain the math logic.

- Local History Sidebar: Automatically saves every calculation to a local JSON database.

- Export Capabilities: Save your step-by-step solutions to .txt or .pdf formats.

- Smart Validation: Detects syntax errors and unmatched parentheses before processing.

- About/Help: Integrated UI dialog for project metadata and member credits.

## 🛠️ Project Structure
Plaintext
Opm/
├── .git/
├── .gitignore
├── .vscode/
├── main.py
├── README.md
├── requirements.txt
├── symbolic_engine.py
├── test_engine.py
├── TEST_PLANv1.md
├── OPM_Symbolic_Math_Generator.exe 
├── venv/
├── symbolic_simplifier/ 
│ ├── __init__.py
│ ├── engine.py
│ ├── main.py
│ ├── parser.py
│ ├── rules/
│ │ ├── __init__.py
│ │ ├── binomial_expansion.py
│ │ ├── combine_like_terms.py
│ │ ├── distributive_property.py
│ │ ├── exponent_rules.py
│ │ ├── factorization.py
│ │ ├── multi_term_distribution.py
│ │ ├── polynomial_simplification.py
│ │ ├── rational_simplification.py
│ │ └── special_products.py
│ ├── ui/
│ │ ├── __init__.py
│ │ └── interface.py
│ └── utils/
│ ├── __init__.py
│ ├── expression_formatter.py
│ └── step_logger.py

## 👥 The Team
Miranda, Jessa Bien T.
Oakes, Kenneth Gabren E.
Pato, Mhira Shane O.