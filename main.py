"""
Root-level entry point for Symbolic Math Application.

This module launches the GUI application from the modular symbolic_simplifier package.
It maintains backward compatibility with existing code.
"""

from symbolic_simplifier.main import run_app

if __name__ == "__main__":
    run_app()
