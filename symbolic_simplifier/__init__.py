"""
Symbolic Simplifier Package

A modular symbolic mathematics simplification engine.
Provides expression parsing, validation, and simplification using algebraic rules.

Modules:
    - engine: Core simplification engine
    - parser: Expression parsing and validation
    - utils: Utility functions for formatting and logging
    - rules: Individual algebraic rule implementations
    - ui: User interface components
"""

# Import main functions at package level for convenience
from .engine import process
from .parser import validate_expression, parse_expression
from .utils.expression_formatter import beautify_str, format_trail

__all__ = [
    'process',
    'validate_expression',
    'parse_expression',
    'beautify_str',
    'format_trail',
]
