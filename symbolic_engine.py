"""
Symbolic Engine (Legacy Compatibility Module)

This module provides backward compatibility by re-exporting the main
process function from the refactored modular symbolic_simplifier package.

The core logic and implementation has been moved to:
    symbolic_simplifier/engine.py
    symbolic_simplifier/parser.py
    symbolic_simplifier/utils/
    symbolic_simplifier/rules/

This file ensures that existing code importing from symbolic_engine
continues to work without modification.
"""

from symbolic_simplifier import process

__all__ = ['process']
