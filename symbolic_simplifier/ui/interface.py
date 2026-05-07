"""
Interface Module

Handles the GUI components and user interaction for the symbolic math simplifier.
Provides the retro-styled UI with input/output panels and control buttons.

Classes:
    - RetroButton: Custom button styled with retro aesthetic
    - SymbolicMathApp: Main application window and UI management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    _HAS_REPORTLAB = True
except ImportError:
    letter = None
    canvas = None
    _HAS_REPORTLAB = False


class RetroButton(tk.Button):
    """Modernized button style with consistent monospace typography."""
    def __init__(self, parent, text, command=None, **kwargs):
        kwargs.setdefault("font", ("Consolas", 11, "bold"))
        kwargs.setdefault("bg", "#35356b")
        kwargs.setdefault("fg", "#FFFFFF")
        kwargs.setdefault("activebackground", "#2a2a55")
        kwargs.setdefault("activeforeground", "#FFFFFF")
        kwargs.setdefault("relief", tk.FLAT)
        kwargs.setdefault("bd", 0)
        kwargs.setdefault("padx", 14)
        kwargs.setdefault("pady", 8)
        kwargs.setdefault("cursor", "hand2")
        super().__init__(parent, text=text, command=command, **kwargs)


def format_recommended_warning(message: str) -> str:
    """Format a recommended next step message for display in the UI."""
    if message.startswith("⚠️"):
        return message
    return f"⚠️ RECOMMENDED: {message}"

    
