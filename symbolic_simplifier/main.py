"""
Main Entry Point for Symbolic Math Simplifier

Launches the GUI application for symbolic expression simplification.
Integrates the modular engine with the retro-styled user interface.
"""

import threading
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont
import json
import os
from datetime import datetime

# Import the core engine and utilities
from . import process
from .engine import process_by_rule
from .ui.interface import RetroButton, format_recommended_warning

# For PDF export (requires reportlab package)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    _HAS_REPORTLAB = True
except ImportError:
    letter = None
    canvas = None
    pdfmetrics = None
    TTFont = None
    _HAS_REPORTLAB = False

_PDF_UNICODE_FONT_NAME = "OPMUnicode"
_PDF_FONT_CANDIDATES = [
    "DejaVuSans.ttf",
    "Arial Unicode MS.ttf",
    "arialuni.ttf",
    "Segoe UI Symbol.ttf",
    "seguisym.ttf",
    "Segoe UI Emoji.ttf",
    "seguiemj.ttf",
    "FreeSerif.ttf",
    "LiberationSans-Regular.ttf",
]


def _find_system_font(filename: str):
    """Search common system font paths for a TrueType font file."""
    if not filename:
        return None
    paths = []
    if os.name == "nt":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        paths.extend([
            os.path.join(windir, "Fonts", filename),
            os.path.join(windir, "Fonts", filename.replace(" ", "")),
        ])
    else:
        paths.extend([
            f"/usr/share/fonts/truetype/{filename}",
            f"/usr/share/fonts/truetype/dejavu/{filename}",
            f"/usr/share/fonts/{filename}",
            f"/usr/local/share/fonts/{filename}",
            os.path.expanduser(f"~/Library/Fonts/{filename}"),
            os.path.expanduser(f"~/.local/share/fonts/{filename}"),
        ])

    for path in paths:
        if path and os.path.isfile(path):
            return path
    return None


def _register_pdf_unicode_font() -> bool:
    """Register a Unicode-capable TTF font for PDF export."""
    if not _HAS_REPORTLAB or pdfmetrics is None or TTFont is None:
        return False

    try:
        pdfmetrics.getFont(_PDF_UNICODE_FONT_NAME)
        return True
    except Exception:
        pass

    for candidate in _PDF_FONT_CANDIDATES:
        font_path = _find_system_font(candidate)
        if font_path:
            try:
                pdfmetrics.registerFont(TTFont(_PDF_UNICODE_FONT_NAME, font_path))
                return True
            except Exception:
                continue

    return False


def _normalize_pdf_text(line: str) -> str:
    """Replace unsupported symbols with ASCII-safe alternatives when no Unicode font is available."""
    replacements = {
        "•": "-",
        "■": "-",
        "→": "->",
        "✓": "[OK]",
        "⚠️": "WARNING:",
        "—": "--",
        "…": "...",
    }
    for src, dst in replacements.items():
        line = line.replace(src, dst)
    return line


class SymbolicMathApp(tk.Widget):
    """Complete Symbolic Math Application with full UI.
    
    Provides a retro-styled interface for symbolic expression simplification
    with support for multiple export formats and a step-by-step solution trail.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("SYMBOLIC MATH GENERATOR v1.0")
        self.root.geometry("1000x750")
        self.root.configure(bg="#e8e8e8")
        self.base_font = ("Consolas", 11)
        self.base_bold = ("Consolas", 12, "bold")
        self.code_font = ("Consolas", 11)
        self.panel_bg = "#f5f5f5"

        # history storage
        self.history = []  # list of dicts: {'expression','final','trail','timestamp'}
        self.history_path = os.path.join(os.getcwd(), "history.json")
        self.is_processing = False
        self.dedicated_panels = []  # list of open dedicated panel windows
        self.compute_button = None
        # compute typical entry width based on placeholder text
        sample_text = "x+99 (2000-01-01 00:00:00)"
        try:
            char_width = tkfont.Font(font=self.code_font).measure('0')
            sample_px = tkfont.Font(font=self.code_font).measure(sample_text)
        except Exception:
            sample_px = 120
        # minimum width for sidebar when empty; use sample width plus padding
        self.min_sidebar_px = sample_px + char_width * 2
        # remember last-used calculated width (never shrink below this)
        self.sidebar_width_px = None
        self.load_history()

        self.build_ui()

    def build_ui(self):
        # create horizontal paned window containing sidebar and main content
        main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill="both", expand=True)
        self.main_container = main_container  # keep reference for toggle

        # content area holds the existing UI elements (add first so sidebar ends up on right)
        self.content_frame = tk.Frame(main_container, bg="#e8e8e8")
        main_container.add(self.content_frame)
        # let the content pane expand to fill available space
        try:
            main_container.paneconfigure(self.content_frame, stretch='always')
        except Exception:
            pass

        # sidebar for history/chat list placed on the right
        self.sidebar_frame = tk.Frame(main_container, bg="#e0e0e0", width=220)
        main_container.add(self.sidebar_frame, minsize=220)
        # keep sidebar from stretching when window is resized
        try:
            main_container.paneconfigure(self.sidebar_frame, stretch='never')
        except Exception:
            pass
        self.history_visible = True

        # RULE ICONS
        tk.Label(self.sidebar_frame, text="RULES", font=self.base_bold, bg="#e0e0e0").pack(pady=(10,0))
        icons_frame = tk.Frame(self.sidebar_frame, bg="#e0e0e0")
        icons_frame.pack(pady=(5,5), padx=5)
        
        # Define rule icons with short labels
        rule_icons = [
            ("Binomial Expansion", "📈", "Binomial"),
            ("Distributive Property", "➗", "Distribute"),
            ("Multi-Term Distribution", "✖️", "Multi-Term"),
            ("Exponent Rules", "🔥", "Exponents"),
            ("Combine Like Terms", "➕", "Combine"),
            ("Rational Expression Simplification", "📐", "Rational"),
            ("Special Products", "🎯", "Special"),
            ("Factorization", "🔧", "Factor"),
            ("Polynomial Simplification", "📊", "Polynomial")
        ]

        for index, (rule_name, icon, label_text) in enumerate(rule_icons):
            icon_container = tk.Frame(icons_frame, bg="#e0e0e0")
            icon_container.grid(row=index // 3, column=index % 3, padx=6, pady=6)

            btn = tk.Button(
                icon_container,
                text=icon,
                font=("Consolas", 14),
                bg="#ffffff",
                fg="#000000",
                relief=tk.RAISED,
                bd=1,
                width=3,
                height=1,
                command=lambda r=rule_name: self.open_dedicated_panel(r)
            )
            btn.pack(padx=2, pady=(0, 2))
            tk.Label(
                icon_container,
                text=label_text,
                font=("Consolas", 8),
                bg="#e0e0e0",
                fg="#333333",
                wraplength=70,
                justify="center"
            ).pack()
            self.add_tooltip(btn, rule_name)

        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill="x", padx=10, pady=(8, 10))

        # HISTORY SIDEBAR
        tk.Label(self.sidebar_frame, text="HISTORY", font=self.base_bold, bg="#e0e0e0").pack(pady=(10,0))
        # container for listbox + scrollbar to keep scrollbar adjacent
        list_container = tk.Frame(self.sidebar_frame, bg="#e0e0e0")
        list_container.pack(fill="both", expand=True, padx=5, pady=5)
        self.history_listbox = tk.Listbox(
            list_container,
            font=self.base_font,
            bg="#ffffff",
            fg="#111111",
            bd=0,
            highlightthickness=1,
            highlightbackground="#c4c4c4",
            selectbackground="#dce7ff",
            activestyle="none"
        )
        self.history_listbox.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        self.history_listbox.bind("<<ListboxSelect>>", self.on_history_select)
        hist_scroll = ttk.Scrollbar(list_container, command=self.history_listbox.yview)
        hist_scroll.pack(side="right", fill="y")
        self.history_listbox.config(yscrollcommand=hist_scroll.set)

        # Action buttons (NEW and CLEAR) - side-by-side
        button_container = tk.Frame(self.sidebar_frame, bg="#e0e0e0")
        button_container.pack(fill="x", padx=4, pady=8)

        # NEW button (primary - filled style)
        tk.Button(
            button_container,
            text="NEW",
            command=self.new_session,
            font=("Consolas", 10, "bold"),
            bg="#0f5f0f",
            fg="#ffffff",
            activebackground="#0b4b3f",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=6,
            pady=4,
            cursor="hand2"
        ).pack(side="left", fill="both", expand=True, padx=(0, 4))

        # CLEAR button (secondary - ghost style)
        tk.Button(
            button_container,
            text="CLEAR",
            command=self.clear_history,
            font=("Consolas", 10, "bold"),
            bg="#e8e8e8",
            fg="#4b4b4b",
            activebackground="#d5d5d5",
            activeforeground="#2a2a2a",
            relief=tk.SOLID,
            bd=1,
            padx=6,
            pady=4,
            cursor="hand2"
        ).pack(side="left", fill="both", expand=True, padx=(4, 0))

        # TITLE BANNER with Option B logo (block mark + serif)
        title_frame = tk.Frame(self.content_frame, bg="#e8e8e8")
        title_frame.pack(fill="x", padx=10, pady=12)

        # Logo container with block mark and text
        logo_frame = tk.Frame(title_frame, bg="#e8e8e8")
        logo_frame.pack(side="left", fill="y", padx=(0, 12))

        # Solid dark square monogram (block mark)
        monogram_canvas = tk.Canvas(
            logo_frame,
            width=56,
            height=56,
            bg="#e8e8e8",
            highlightthickness=0
        )
        monogram_canvas.pack(side="left", padx=(0, 8))
        monogram_canvas.create_rectangle(0, 0, 56, 56, fill="#1a1a1a", outline="#1a1a1a")
        monogram_canvas.create_text(
            28, 28,
            text="O",
            font=("Garamond", 32, "bold"),
            fill="#ffffff",
            anchor="center"
        )

        # Text section next to monogram
        text_frame = tk.Frame(logo_frame, bg="#e8e8e8")
        text_frame.pack(side="left", fill="both", expand=True)

        tk.Label(
            text_frame,
            text="OPM",
            font=("Consolas", 14, "bold"),
            bg="#e8e8e8",
            fg="#1f1f1f",
            anchor="w"
        ).pack(anchor="w")

        tk.Label(
            text_frame,
            text="SYMBOLIC MATH GENERATOR",
            font=("Consolas", 9, "italic"),
            bg="#e8e8e8",
            fg="#4b4b4b",
            anchor="w"
        ).pack(anchor="w")

        # Utility actions on the right side of the header
        util_frame = tk.Frame(title_frame, bg="#e8e8e8")
        util_frame.pack(side="right", anchor="n")

        about_btn = tk.Button(
            util_frame,
            text="ⓘ",
            font=("Consolas", 14),
            bg="#e8e8e8",
            fg="#6d6d6d",
            activebackground="#e8e8e8",
            activeforeground="#1f1f1f",
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            padx=6,
            pady=6,
            cursor="hand2",
            command=self.show_about
        )
        about_btn.pack(side="left", padx=(0, 8))
        self.add_tooltip(about_btn, "About / Help")

        # toggle button for history sidebar
        self.toggle_btn = RetroButton(util_frame, "☰", command=self.toggle_history, width=3)
        self.toggle_btn.pack(side="left")

        # INPUT PANEL
        input_frame = tk.Frame(self.content_frame, bg=self.panel_bg, bd=1, relief=tk.SOLID)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(input_frame, text="INPUT EXPRESSION:", font=self.base_bold, bg=self.panel_bg, fg="#1f1f1f").pack(side="left", padx=10, pady=10)
        
        self.expression_entry = tk.Entry(
            input_frame,
            font=self.base_font,
            bg="#ffffff",
            fg="#000000",
            insertbackground="#000000",
            relief=tk.FLAT,
            bd=0
        )
        self.expression_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10, ipady=6)

        # BUTTON PANEL
        buttons_inner = tk.Frame(self.content_frame, bg="#e8e8e8")
        buttons_inner.pack(pady=12)
        
        self.compute_button = RetroButton(
            buttons_inner,
            "▶ COMPUTE",
            command=self.compute_expression,
            bg="#0f5f0f",
            activebackground="#0b4b3f",
            fg="#ffffff"
        )
        self.compute_button.pack(side="left", padx=6)
        RetroButton(buttons_inner, "🧹 CLEAR", command=self.clear_fields, bg="#35356b", activebackground="#2a2a55").pack(side="left", padx=6)
        RetroButton(buttons_inner, "📋 COPY", command=self.copy_trail, bg="#35356b", activebackground="#2a2a55").pack(side="left", padx=6)
        RetroButton(buttons_inner, "💾 EXPORT", command=self.export_trail_prompt, bg="#35356b", activebackground="#2a2a55").pack(side="left", padx=6)

        # PROCESSING STATUS PANEL (above Final Answer)
        status_frame = tk.Frame(self.content_frame, bg="#e8e8e8")
        status_frame.pack(fill="x", padx=10, pady=(5, 8))

        self.status_label = tk.Label(
            status_frame,
            text="● IDLE",
            font=self.base_font,
            bg="#f5f5f5",
            fg="#4b4b4b",
            relief=tk.SOLID,
            bd=1,
            padx=8,
            pady=4
        )
        self.status_label.pack(side="left", padx=5)

        self.progress_bar = ttk.Progressbar(status_frame, mode="indeterminate")
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=6, pady=4)

        # FINAL ANSWER PANEL
        final_frame = tk.Frame(self.content_frame, bg=self.panel_bg, bd=1, relief=tk.SOLID)
        final_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(final_frame, text="✅ FINAL ANSWER", font=self.base_bold, bg=self.panel_bg, fg="#0f5f0f").pack(anchor="w", padx=10, pady=10)

        self.final_answer_label = tk.Label(
            final_frame,
            text="[Awaiting Input]",
            font=self.base_bold,
            bg="#E9E9DF",
            fg="#000000",
            wraplength=900,
            justify="left",
            pady=8,
            padx=8,
            relief=tk.FLAT
        )
        self.final_answer_label.pack(fill="x", padx=5, pady=(0, 5))

        # SOLUTION TRAIL PANEL
        trail_frame = tk.Frame(self.content_frame, bg=self.panel_bg, bd=1, relief=tk.SOLID)
        trail_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        tk.Label(trail_frame, text="SOLUTION TRAIL:", font=self.base_bold, bg=self.panel_bg, fg="#1f1f1f").pack(anchor="w", padx=10, pady=10)

        trail_inner = tk.Frame(trail_frame, bg=self.panel_bg)
        trail_inner.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        
        self.trail_text = tk.Text(
            trail_inner,
            wrap="word",
            font=self.base_font,
            bg="#ffffff",
            fg="#000000",
            insertbackground="#000000",
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=8
        )
        self.trail_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(trail_inner, command=self.trail_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.trail_text.config(yscrollcommand=scrollbar.set, state="disabled")
        self.trail_text.tag_config("header_given", font=self.base_bold, foreground="#0b6c4f", spacing3=4)
        self.trail_text.tag_config("header_method", font=self.base_bold, foreground="#a56c00", spacing3=4)
        self.trail_text.tag_config("header_steps", font=self.base_bold, foreground="#17418a", spacing3=4)
        self.trail_text.tag_config("header_final", font=self.base_bold, foreground="#0f5f0f", spacing3=4)
        self.trail_text.tag_config("header_verify", font=self.base_bold, foreground="#5b3b7b", spacing3=4)
        self.trail_text.tag_config("header_summary", font=self.base_bold, foreground="#4b4b18", spacing3=4)
        self.trail_text.tag_config("section", foreground="#0f0f0f", lmargin1=10, lmargin2=10)
        self.trail_text.tag_config("section_card", background="#f7f9fc", lmargin1=10, lmargin2=10, spacing1=4, spacing3=4)
        self.trail_text.tag_config("quote", font=self.base_bold, foreground="#2d2d2d")
        self.trail_text.tag_config("status_ok", font=self.base_bold, foreground="#0b6c4f")

        # populate history listbox (history loaded during init)
        self.update_history_list()

        # collapse history by default
        self.toggle_history(initial=True)

    def add_tooltip(self, widget, text):
        """Add a tooltip to a widget."""
        def enter(event):
            self.tooltip = tk.Toplevel()
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry("+0+0")
            label = tk.Label(self.tooltip, text=text, bg="#ffffe0", relief="solid", borderwidth=1, font=("Consolas", 8))
            label.pack()
            # Position tooltip near the widget
            x = event.widget.winfo_rootx() + 20
            y = event.widget.winfo_rooty() + event.widget.winfo_height() + 5
            self.tooltip.wm_geometry(f"+{x}+{y}")
        
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def open_dedicated_panel(self, rule_name):
        """Open a dedicated panel for a specific rule."""
        # Limit to 4 concurrent panels
        if len(self.dedicated_panels) >= 4:
            messagebox.showwarning("PANEL LIMIT", "Maximum 4 dedicated panels allowed. Close some panels first.", parent=self.root)
            return
        
        # Create new window
        panel = tk.Toplevel(self.root)
        panel.title(f"{rule_name} Panel")
        panel.geometry("800x600")
        panel.configure(bg="#e8e8e8")
        
        # Track the panel
        self.dedicated_panels.append(panel)
        panel.protocol("WM_DELETE_WINDOW", lambda: self.close_dedicated_panel(panel))
        
        # Title
        title_frame = tk.Frame(panel, bg="#e8e8e8")
        title_frame.pack(fill="x", padx=10, pady=12)
        
        title_label = tk.Label(
            title_frame,
            text=f"{rule_name.upper()} PANEL",
            font=("Consolas", 15, "bold"),
            bg="#e8e8e8",
            fg="#1f1f1f",
            justify="left"
        )
        title_label.pack(side="left")
        
        # Input panel
        input_frame = tk.Frame(panel, bg=self.panel_bg, bd=1, relief=tk.SOLID)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(input_frame, text="INPUT EXPRESSION:", font=self.base_bold, bg=self.panel_bg, fg="#1f1f1f").pack(side="left", padx=10, pady=10)
        
        expr_entry = tk.Entry(
            input_frame,
            font=self.code_font,
            bg="#ffffff",
            fg="#000000",
            insertbackground="#000000",
            relief=tk.FLAT,
            bd=0
        )
        expr_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10, ipady=6)
        
        # Compute button
        RetroButton(input_frame, "▶ APPLY RULE", command=lambda: self.compute_dedicated(panel, expr_entry, rule_name), bg="#0f5f0f", activebackground="#0b4b3f", fg="#ffffff").pack(side="right", padx=8, pady=10)
        
        # Button panel (similar to main panel)
        buttons_inner = tk.Frame(panel, bg="#e8e8e8")
        buttons_inner.pack(pady=12)
        
        RetroButton(buttons_inner, "🧹 CLEAR", command=lambda: self.clear_dedicated_fields(panel)).pack(side="left", padx=5)
        RetroButton(buttons_inner, "📋 COPY", command=lambda: self.copy_dedicated_trail(panel)).pack(side="left", padx=5)
        RetroButton(buttons_inner, "💾 EXPORT", command=lambda: self.export_dedicated_trail(panel)).pack(side="left", padx=5)
        
        # Processing status panel
        status_frame = tk.Frame(panel, bg="#e8e8e8")
        status_frame.pack(fill="x", padx=10, pady=(5, 8))
        
        status_label = tk.Label(
            status_frame,
            text="● IDLE",
            font=self.base_font,
            bg="#f5f5f5",
            fg="#4b4b4b",
            relief=tk.SOLID,
            bd=1,
            padx=8,
            pady=4
        )
        status_label.pack(side="left", padx=5)
        
        progress_bar = ttk.Progressbar(status_frame, mode="indeterminate")
        progress_bar.pack(side="left", fill="x", expand=True, padx=6)
        
        # Final answer panel
        final_frame = tk.Frame(panel, bg=self.panel_bg, bd=1, relief=tk.SOLID)
        final_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(final_frame, text="✅ FINAL ANSWER", font=self.base_bold, bg=self.panel_bg, fg="#0f5f0f").pack(anchor="w", padx=10, pady=10)
        
        final_label = tk.Label(
            final_frame,
            text="[Awaiting Input]",
            font=self.base_bold,
            bg="#ffffff",
            fg="#000000",
            wraplength=700,
            justify="left",
            pady=8,
            padx=8,
            relief=tk.FLAT
        )
        final_label.pack(fill="x", padx=5, pady=(0, 5))
        
        # Solution trail panel
        trail_frame = tk.Frame(panel, bg=self.panel_bg, bd=1, relief=tk.SOLID)
        trail_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        tk.Label(trail_frame, text="SOLUTION TRAIL:", font=self.base_bold, bg=self.panel_bg, fg="#1f1f1f").pack(anchor="w", padx=10, pady=10)

        trail_inner = tk.Frame(trail_frame, bg=self.panel_bg)
        trail_inner.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        
        trail_text = tk.Text(
            trail_inner,
            wrap="word",
            font=self.base_font,
            bg="#ffffff",
            fg="#000000",
            insertbackground="#000000",
            relief=tk.FLAT,
            bd=0,
            state="disabled",
            padx=8,
            pady=8
        )
        trail_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(trail_inner, command=trail_text.yview)
        scrollbar.pack(side="right", fill="y")
        trail_text.config(yscrollcommand=scrollbar.set)
        
        trail_text.tag_config("header_given", font=self.base_bold, foreground="#0b6c4f")
        trail_text.tag_config("header_method", font=self.base_bold, foreground="#a56c00")
        trail_text.tag_config("header_steps", font=self.base_bold, foreground="#17418a")
        trail_text.tag_config("header_final", font=self.base_bold, foreground="#0f5f0f")
        trail_text.tag_config("header_verify", font=self.base_bold, foreground="#5b3b7b")
        trail_text.tag_config("header_summary", font=self.base_bold, foreground="#4b4b18")
        trail_text.tag_config("section", foreground="#0f0f0f", lmargin1=10, lmargin2=10)
        trail_text.tag_config("section_card", background="#f7f9fc", lmargin1=10, lmargin2=10, spacing1=4, spacing3=4)
        trail_text.tag_config("quote", font=self.base_bold)
        trail_text.tag_config("status_ok", font=self.base_bold, foreground="#0b6c4f")
        
        # Store references in panel
        panel.expr_entry = expr_entry
        panel.final_label = final_label
        panel.trail_text = trail_text
        panel.status_label = status_label
        panel.progress_bar = progress_bar
        panel.rule_name = rule_name
        
        # Store badge map for dedicated panels
        panel.badge_map = {
            "GIVEN": "◉ GIVEN",
            "METHOD": "◐ METHOD",
            "STEPS": "◈ STEPS",
            "FINAL ANSWER": "✔ FINAL ANSWER",
            "VERIFICATION": "[?] VERIFICATION",
            "SUMMARY": "▥ SUMMARY"
        }
        panel.header_tag_map = {
            "GIVEN": "header_given",
            "METHOD": "header_method",
            "STEPS": "header_steps",
            "FINAL ANSWER": "header_final",
            "VERIFICATION": "header_verify",
            "SUMMARY": "header_summary"
        }

    def close_dedicated_panel(self, panel):
        """Close a dedicated panel."""
        if panel in self.dedicated_panels:
            self.dedicated_panels.remove(panel)
        panel.destroy()

    def compute_dedicated(self, panel, expr_entry, rule_name):
        """Compute expression using only the specified rule."""
        expr = expr_entry.get().strip()
        if not expr:
            messagebox.showwarning("INPUT ERROR", "[!] Please enter an expression.", parent=panel)
            return
        
        # Update status and start progress
        panel.status_label.config(text="⏳ PROCESSING...", fg="#0a5fa0")
        panel.progress_bar.start(10)
        
        try:
            result = process_by_rule(expr, rule_name)
            
            if result["status"] == "success":
                final_text = result["final_answer"]
                if result.get("final_warning"):
                    final_text = f"{format_recommended_warning(result['final_warning'])}\n{final_text}"
                panel.final_label.config(text=final_text)
                panel.trail_text.config(state="normal")
                panel.trail_text.delete(1.0, tk.END)
                
                # Render formatted trail with icons and styling (same as main trail)
                verification_ok_indices = set()
                sections = result["formatted_trail"].split("\n\n")
                for section in sections:
                    if section.strip():
                        lines = section.strip().split("\n")
                        header_name = lines[0].upper()
                        badge = panel.badge_map.get(header_name, "❓ " + lines[0].upper())
                        header_tag = panel.header_tag_map.get(header_name, "header")
                        panel.trail_text.insert(tk.END, f"{badge}\n", header_tag)
                        content_lines = lines[1:]
                        
                        # Handle verification status lines
                        if header_name == "VERIFICATION":
                            for i, line in enumerate(content_lines):
                                match = re.match(r"^\s*-?\s*\*?\s*Status\s*:\s*(.+)$", line, re.IGNORECASE)
                                if match:
                                    status = match.group(1).strip()
                                    icon = "[OK]" if status.lower() == "passed" else "[XX]"
                                    content_lines[i] = f" {icon} {status}"
                                    if status.lower() == "passed":
                                        verification_ok_indices.add(i)
                        
                        for idx, line in enumerate(content_lines):
                            line_to_insert = line
                            if idx < len(content_lines) - 1:
                                line_to_insert += "\n"
                            else:
                                line_to_insert += "\n\n"
                            panel.trail_text.insert(tk.END, line_to_insert, ("section", "section_card"))
                            
                            # Apply green bold tag to [OK] status lines
                            if header_name == "VERIFICATION" and idx in verification_ok_indices:
                                ok_match = re.search(r'\[OK\].*', line)
                                if ok_match:
                                    found = panel.trail_text.search(ok_match.group(), tk.END + "-1 lines", backwards=True, exact=False)
                                    if found:
                                        end_pos = f"{found}+{len(ok_match.group())} chars"
                                        panel.trail_text.tag_add("status_ok", found, end_pos)
                            
                            # Bold labels (text ending with colon) but skip sub-items
                            stripped = line.lstrip()
                            if ':' in stripped and not stripped[0] in '-ab(' and '[OK]' not in line:
                                label_match = re.match(r'^(\s*)(.+?:)', line)
                                if label_match:
                                    label_text = label_match.group(2)
                                    found = panel.trail_text.search(label_text, tk.END + "-1 lines", backwards=True, exact=False)
                                    if found:
                                        end_pos = f"{found}+{len(label_text)} chars"
                                        panel.trail_text.tag_add("quote", found, end_pos)
                
                panel.trail_text.config(state="disabled")
            else:
                messagebox.showerror("ERROR", result["error_message"], parent=panel)
                
        except Exception as e:
            messagebox.showerror("ERROR", f"Processing failed: {str(e)}", parent=panel)
        finally:
            # Reset status
            panel.status_label.config(text="✔ IDLE", fg="#0f5f0f")
            panel.progress_bar.stop()

    # ---- dedicated panel methods ---------------------------------------------
    def clear_dedicated_fields(self, panel):
        """Clear all input and output fields in dedicated panel."""
        panel.expr_entry.delete(0, tk.END)
        panel.final_label.config(text="[Awaiting Input]")
        panel.trail_text.config(state="normal")
        panel.trail_text.delete("1.0", tk.END)
        panel.trail_text.config(state="disabled")
        panel.status_label.config(text="● IDLE", fg="#4b4b4b")
        panel.progress_bar.stop()
        panel.trail_text.delete("1.0", tk.END)
        panel.trail_text.config(state="disabled")

    def copy_dedicated_trail(self, panel):
        """Copy the solution trail from dedicated panel to clipboard."""
        trail_content = panel.trail_text.get("1.0", tk.END).strip()
        if trail_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(trail_content)
            self.show_info_dialog("[✓] Solution trail copied to clipboard.", "Copy Successful")

    def export_dedicated_trail(self, panel):
        """Export the solution trail from dedicated panel."""
        trail_content = panel.trail_text.get("1.0", tk.END).strip()
        if not trail_content:
            self.show_info_dialog("[!] No trail to export.", "Export Failed")
            return

        fmt = self.choose_export_format()
        if fmt == 'pdf':
            self.export_pdf(trail_content)
        elif fmt == 'txt':
            self.export_txt(trail_content)

    def compute_expression(self):
        """Entry point: start background processing and show progress."""
        if self.is_processing:
            return

        expr = self.expression_entry.get().strip()
        if not expr:
            messagebox.showwarning("INPUT ERROR", "[!] Please enter an expression.", parent=self.root)
            return

        self.is_processing = True
        self.status_label.config(text="⏳ PROCESSING...", fg="#0a5fa0")
        self.progress_bar.start(10)
        self.compute_button.config(state="disabled")

        thread = threading.Thread(target=self._compute_expression_thread, args=(expr,), daemon=True)
        thread.start()

    def _compute_expression_thread(self, expr):
        try:
            result = process(expr)
        except Exception as e:
            result = {
                "status": "error",
                "error_message": str(e),
                "final_answers": {},
                "formatted_trail": "",
            }

        self.root.after(0, lambda: self._on_compute_complete(expr, result))

    def _on_compute_complete(self, expr, result):
        self.trail_text.config(state="normal")
        self.trail_text.delete("1.0", tk.END)

        if result["status"] == "success":
            factored = result["final_answers"]["factored_form"]
            canonical = result["final_answers"]["canonical_form"]
            final_text = f"✓ FACTORED: {factored}\n✓ CANONICAL: {canonical}"
            self.final_answer_label.config(text=final_text)

            badge_map = {
                "GIVEN": "◉ GIVEN",
                "METHOD": "◐ METHOD",
                "STEPS": "◈ STEPS",
                "FINAL ANSWER": "✔ FINAL ANSWER",
                "VERIFICATION": "[?] VERIFICATION",
                "SUMMARY": "▥ SUMMARY"
            }

            header_tag_map = {
                "GIVEN": "header_given",
                "METHOD": "header_method",
                "STEPS": "header_steps",
                "FINAL ANSWER": "header_final",
                "VERIFICATION": "header_verify",
                "SUMMARY": "header_summary"
            }

            sections = result["formatted_trail"].split("\n\n")
            for section in sections:
                if section.strip():
                    lines = section.strip().split("\n")
                    header_name = lines[0].upper()
                    badge = badge_map.get(header_name, "❓ " + lines[0].upper())
                    header_tag = header_tag_map.get(header_name, "header")
                    self.trail_text.insert(tk.END, f"{badge}\n", header_tag)
                    content_lines = lines[1:]

                    verification_ok_indices = set()
                    if header_name == "VERIFICATION":
                        for i, line in enumerate(content_lines):
                            match = re.match(r"^\s*-?\s*\*?\s*Status\s*:\s*(.+)$", line, re.IGNORECASE)
                            if match:
                                status = match.group(1).strip()
                                icon = "[OK]" if status.lower() == "passed" else "[XX]"
                                content_lines[i] = f" {icon} {status}"
                                if status.lower() == "passed":
                                    verification_ok_indices.add(i)

                    for idx, line in enumerate(content_lines):
                        line_to_insert = line
                        if idx < len(content_lines) - 1:
                            line_to_insert += "\n"
                        else:
                            line_to_insert += "\n\n"

                        self.trail_text.insert(tk.END, line_to_insert, ("section", "section_card"))

                        # Apply green bold tag to [OK] status lines
                        if header_name == "VERIFICATION" and idx in verification_ok_indices:
                            ok_match = re.search(r'\[OK\].*', line)
                            if ok_match:
                                found = self.trail_text.search(ok_match.group(), tk.END + "-1 lines", backwards=True, exact=False)
                                if found:
                                    end_pos = f"{found}+{len(ok_match.group())} chars"
                                    self.trail_text.tag_add("status_ok", found, end_pos)

                        # Bold labels (text ending with colon) but skip sub-items
                        stripped = line.lstrip()
                        if ':' in stripped and not stripped[0] in '-ab(' and '[OK]' not in line:
                            label_match = re.match(r'^(\s*)(.+?:)', line)
                            if label_match:
                                label_text = label_match.group(2)
                                found = self.trail_text.search(label_text, tk.END + "-1 lines", backwards=True, exact=False)
                                if found:
                                    end_pos = f"{found}+{len(label_text)} chars"
                                    self.trail_text.tag_add("quote", found, end_pos)
        else:
            self.final_answer_label.config(text="[ERROR] Failed to compute")
            err_msg = result.get("error_message") or "Failed to compute expression. Check syntax."
            messagebox.showerror("COMPUTATION ERROR", err_msg, parent=self.root)

        trail_content = self.trail_text.get("1.0", tk.END).strip()
        try:
            hist_final = self.final_answer_label.cget("text")
            self.add_history_entry(expr, hist_final, trail_content)
        except Exception:
            pass

        self.trail_text.see("1.0")
        self.trail_text.config(state="disabled")

        self.is_processing = False
        self.status_label.config(text="✔ IDLE", fg="#0f5f0f")
        self.progress_bar.stop()
        self.compute_button.config(state="normal")

    def clear_fields(self):
        """Clear all input and output fields."""
        self.expression_entry.delete(0, tk.END)
        self.final_answer_label.config(text="[Awaiting Input]")
        self.trail_text.config(state="normal")
        self.trail_text.delete("1.0", tk.END)
        self.trail_text.config(state="disabled")
        self.status_label.config(text="● IDLE", fg="#4b4b4b")
        self.progress_bar.stop()

    def copy_trail(self):
        """Copy the simplification trail to clipboard."""
        trail_content = self.trail_text.get("1.0", tk.END).strip()

        if not trail_content:
            self.show_info_dialog(
                "[!] Solution trail is empty.\nCompute an expression first.",
                "Copy Error"
            )
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(trail_content)
        self.show_info_dialog("[✓] Solution trail copied to clipboard!", "Copy Status")

    def export_trail_prompt(self):
        """Ask user whether to export TXT or PDF"""
        trail_content = self.trail_text.get("1.0", tk.END).strip()

        if not trail_content:
            self.show_info_dialog(
                "[!] Nothing to export.\nCompute an expression first.",
                "Export Error"
            )
            return

        if _HAS_REPORTLAB:
            fmt = self.choose_export_format()

            if fmt == 'pdf':
                self.export_pdf(trail_content)

            elif fmt == 'txt':
                self.export_txt(trail_content)

        else:
            self.show_info_dialog(
                "[!] PDF export requires the 'reportlab' package.\n"
                "Install it via pip and restart the application.",
                "Missing Dependency"
            )
            self.export_txt(trail_content)

    def choose_export_format(self):
        """Display a retro dialog that returns 'pdf', 'txt', or None."""

        dlg = tk.Toplevel(self.root)
        dlg.title("Export Format")
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(bg="#d1d1d1")

        result = {"format": None}

        def set_fmt(fmt):
            result["format"] = fmt
            dlg.destroy()

        dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)

        frame = tk.Frame(dlg, bg="#d1d1d1", padx=20, pady=15)
        frame.pack()

        tk.Label(
            frame,
            text="[i] Choose export format:",
            font=self.base_font,
            bg="#d1d1d1"
        ).pack(pady=(0, 10))

        btn_frame = tk.Frame(frame, bg="#d1d1d1")
        btn_frame.pack()

        RetroButton(btn_frame, "PDF", command=lambda: set_fmt("pdf")).pack(side="left", padx=6)
        RetroButton(btn_frame, "TXT", command=lambda: set_fmt("txt")).pack(side="left", padx=6)
        RetroButton(btn_frame, "CANCEL", command=dlg.destroy).pack(side="left", padx=6)

        dlg.update_idletasks()

        w = dlg.winfo_width()
        h = dlg.winfo_height()

        x = self.root.winfo_rootx() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - h) // 2

        dlg.geometry(f"+{x}+{y}")

        self.root.wait_window(dlg)

        return result["format"]

    def export_txt(self, content):
        """Export simplification trail as text file."""

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="[SAVE] Solution Trail As"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.show_info_dialog(
                    f"[✓] Solution trail saved to:\n{file_path}",
                    "Export Successful"
                )

            except Exception as e:
                self.show_info_dialog(
                    f"[!] Could not save file:\n{str(e)}",
                    "Export Failed"
                )

    def export_pdf(self, content):
        """Export simplification trail as PDF file."""

        if not _HAS_REPORTLAB:
            self.show_info_dialog(
                "[!] ReportLab is not available; cannot create PDF.",
                "Export Failed"
            )
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
            title="[SAVE] Solution Trail As PDF"
        )

        if file_path:
            try:
                font_registered = _register_pdf_unicode_font()
                default_font = _PDF_UNICODE_FONT_NAME if font_registered else "Courier"

                c = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter
                y = height - 40

                for line in content.split("\n"):
                    if not font_registered:
                        line = _normalize_pdf_text(line)

                    if line.startswith("GIVEN") or line.startswith("METHOD") or line.startswith("STEPS"):
                        c.setFont(default_font, 12)
                        c.setFillColorRGB(0, 0.5, 0)
                    elif line.startswith("FINAL ANSWER") or line.startswith("VERIFICATION") or line.startswith("SUMMARY"):
                        c.setFont(default_font, 12)
                        c.setFillColorRGB(0, 0, 0.5)
                    else:
                        c.setFont(default_font, 10)
                        c.setFillColorRGB(0, 0, 0)

                    c.drawString(40, y, line)
                    y -= 14

                    if y < 40:
                        c.showPage()
                        y = height - 40

                c.save()

                self.show_info_dialog(
                    f"[✓] Solution trail saved as PDF:\n{file_path}",
                    "Export Successful"
                )

            except Exception as e:
                self.show_info_dialog(
                    f"[!] Could not save PDF:\n{str(e)}",
                    "Export Failed"
                )

    def show_info_dialog(self, message, title="Information"):
        """Reusable retro info dialog."""

        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(bg="#d1d1d1")

        def close():
            dlg.destroy()

        dlg.protocol("WM_DELETE_WINDOW", close)

        frame = tk.Frame(dlg, bg="#d1d1d1", padx=20, pady=15)
        frame.pack()

        tk.Label(
            frame,
            text=message,
            font=self.base_font,
            bg="#d1d1d1",
            justify="center"
        ).pack(pady=(0, 10))

        RetroButton(frame, "OK", command=close).pack()

        dlg.update_idletasks()

        w = dlg.winfo_width()
        h = dlg.winfo_height()

        x = self.root.winfo_rootx() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - h) // 2

        dlg.geometry(f"+{x}+{y}")

        dlg.bind("<Return>", lambda e: close())
        dlg.bind("<Escape>", lambda e: close())

        self.root.wait_window(dlg)

    def show_about(self):
        """Show the project About / Help dialog."""

        dlg = tk.Toplevel(self.root)
        dlg.title("About / Help")
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(bg="#d1d1d1")
        dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)

        frame = tk.Frame(dlg, bg="#d1d1d1", padx=24, pady=18)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="Project Name:",
            font=self.base_bold,
            bg="#d1d1d1",
            fg="#000000",
            anchor="w"
        ).pack(fill="x")

        tk.Label(
            frame,
            text="Symbolic: Simplify Expression Generator (SymPy)",
            font=("Consolas", 11),
            bg="#d1d1d1",
            fg="#1a1a1a",
            anchor="w"
        ).pack(fill="x", pady=(0, 6))

        tk.Label(
            frame,
            text="SYMBOLIC MATH GENERATOR",
            font=("Consolas", 10, "italic"),
            bg="#d1d1d1",
            fg="#444444",
            anchor="w"
        ).pack(fill="x", pady=(0, 12))

        tk.Label(
            frame,
            text="Members:",
            font=self.base_bold,
            bg="#d1d1d1",
            fg="#000000",
            anchor="w"
        ).pack(fill="x")

        tk.Label(
            frame,
            text="Miranda, Jessa Bien T.\nOakes, Kenneth Gabren E.\nPato, Mhira Shane O.",
            font=self.base_font,
            bg="#d1d1d1",
            fg="#1a1a1a",
            justify="left",
            anchor="w"
        ).pack(fill="x", pady=(0, 12))

        tk.Label(
            frame,
            text="Version:",
            font=self.base_bold,
            bg="#d1d1d1",
            fg="#000000",
            anchor="w"
        ).pack(fill="x")

        tk.Label(
            frame,
            text="Version 1",
            font=self.base_font,
            bg="#d1d1d1",
            fg="#000000",
            anchor="w"
        ).pack(fill="x", pady=(0, 16))

        button_frame = tk.Frame(frame, bg="#d1d1d1")
        button_frame.pack(fill="x")

        RetroButton(button_frame, "CLOSE", command=dlg.destroy, width=10).pack(side="right")

        dlg.update_idletasks()

        w = dlg.winfo_width()
        h = dlg.winfo_height()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - h) // 2
        dlg.geometry(f"+{x}+{y}")

        dlg.bind("<Return>", lambda e: dlg.destroy())
        dlg.bind("<Escape>", lambda e: dlg.destroy())

        self.root.wait_window(dlg)

    # ---- history management -------------------------------------------------
    def load_history(self):
        """Load history from disk (history.json)."""
        try:
            if os.path.exists(self.history_path):
                with open(self.history_path, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except Exception:
            # in case of corrupt file just start fresh
            self.history = []
        self.update_history_list()

    def save_history(self):
        """Persist current history list to disk."""
        try:
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            # if saving fails, we log to console but continue
            print("Failed to save history:", e)

    def add_history_entry(self, expr, final_text, trail_text):
        """Add a new record to history and refresh sidebar."""
        entry = {
            "expression": expr,
            "final": final_text,
            "trail": trail_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # insert at front so newest appear top
        self.history.insert(0, entry)
        self.update_history_list()
        self.save_history()

    def update_history_list(self):
        """Redraw listbox contents from history array and adjust sizing."""
        if not hasattr(self, "history_listbox"):
            return
        self.history_listbox.delete(0, tk.END)
        # track maximum width in pixels
        max_pixel = 0
        char_width = tkfont.Font(font=self.code_font).measure('0')
        for entry in self.history:
            # avoid unnecessary padding after timestamp
            label = f"{entry['expression']} ({entry['timestamp']})"
            self.history_listbox.insert(tk.END, label)
            try:
                pw = tkfont.Font(font=self.code_font).measure(label)
                if pw > max_pixel:
                    max_pixel = pw
            except Exception:
                pass

        # adjust sizes if we found something
        if max_pixel > 0:
            # the listbox will fill its parent; no need to set width here
            pass

            # compute exact desired pixel width including a bit of padding
            desired_px = max_pixel + (2 * char_width)
            # enforce minimum
            if hasattr(self, 'min_sidebar_px'):
                desired_px = max(desired_px, self.min_sidebar_px)
            # also ensure we don't shrink below previously stored sidebar_width_px
            if self.sidebar_width_px is not None:
                desired_px = max(desired_px, self.sidebar_width_px)

            self.sidebar_frame.config(width=desired_px)
            self.current_sidebar_width_px = desired_px
            self.sidebar_width_px = desired_px
            try:
                self.main_container.paneconfigure(self.sidebar_frame, minsize=desired_px, width=desired_px)
            except Exception:
                pass
            if self.history_visible:
                    # width has already been applied via paneconfigure; update and move sash
                    self.main_container.update_idletasks()
                    try:
                        total = self.root.winfo_width()
                        self.main_container.sash_place(0, total - desired_px, 0)
                    except Exception:
                        pass
        else:
            # no entries; preserve existing width if we have one
            if self.sidebar_width_px is None:
                # first time, give it the minimum
                self.sidebar_width_px = self.min_sidebar_px
            # also ensure current_sidebar reflects
            self.current_sidebar_width_px = self.sidebar_width_px
            try:
                self.main_container.paneconfigure(self.sidebar_frame, minsize=self.sidebar_width_px, width=self.sidebar_width_px)
            except Exception:
                pass
    def on_history_select(self, event):
        """Load a selected history entry into the main view."""
        sel = self.history_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        entry = self.history[idx]
        # display data
        self.expression_entry.delete(0, tk.END)
        self.expression_entry.insert(0, entry["expression"])
        self.final_answer_label.config(text=entry["final"])
        self.trail_text.config(state="normal")
        self.trail_text.delete("1.0", tk.END)
        self.trail_text.insert(tk.END, entry["trail"])
        self.trail_text.config(state="disabled")

    def new_session(self):
        """Prepare UI for a new computation (clear inputs but keep history)."""
        self.clear_fields()
        # clear any selection
        self.history_listbox.selection_clear(0, tk.END)


    def clear_history(self):
        """Remove all saved history from memory and disk using a custom dialog."""

        # If history is empty
        if not self.history:
            self.show_history_empty()
            return

        result = self.confirm_clear_history()

        if result:
            self.history = []
            self.update_history_list()

            try:
                if os.path.exists(self.history_path):
                    os.remove(self.history_path)
            except Exception:
                pass
    
    def confirm_clear_history(self):
        """Custom retro confirmation dialog."""
        
        dlg = tk.Toplevel(self.root)
        dlg.title("Confirm")
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(bg="#d1d1d1")

        result = {"value": False}

        def confirm():
            result["value"] = True
            dlg.destroy()

        def cancel():
            dlg.destroy()

        # X button acts like cancel
        dlg.protocol("WM_DELETE_WINDOW", cancel)

        frame = tk.Frame(dlg, bg="#d1d1d1", padx=20, pady=15)
        frame.pack()

        tk.Label(
            frame,
            text="[i] Clear all history?\nThis cannot be undone.",
            font=self.base_font,
            bg="#d1d1d1",
            justify="center"
        ).pack(pady=(0, 10))

        btn_frame = tk.Frame(frame, bg="#d1d1d1")
        btn_frame.pack()

        RetroButton(btn_frame, "YES", command=confirm).pack(side="left", padx=6)
        RetroButton(btn_frame, "NO", command=cancel).pack(side="left", padx=6)

        # center dialog
        dlg.update_idletasks()
        w = dlg.winfo_width()
        h = dlg.winfo_height()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - h) // 2
        dlg.geometry(f"+{x}+{y}")

        self.root.wait_window(dlg)

        return result["value"]
    
    def show_history_empty(self):
        """Retro dialog informing the user history is empty."""

        dlg = tk.Toplevel(self.root)
        dlg.title("History")
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(bg="#d1d1d1")

        def close():
            dlg.destroy()

        dlg.protocol("WM_DELETE_WINDOW", close)

        frame = tk.Frame(dlg, bg="#d1d1d1", padx=20, pady=15)
        frame.pack()

        tk.Label(
            frame,
            text="[i] There are no previous records to clear.",
            font=self.base_font,
            bg="#d1d1d1",
            justify="center"
        ).pack(pady=(0, 10))

        btn_frame = tk.Frame(frame, bg="#d1d1d1")
        btn_frame.pack()

        RetroButton(btn_frame, "OK", command=close).pack(padx=6)

        # center dialog
        dlg.update_idletasks()
        w = dlg.winfo_width()
        h = dlg.winfo_height()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - h) // 2
        dlg.geometry(f"+{x}+{y}")

        self.root.wait_window(dlg)

    def toggle_history(self, initial=False):
        """Show or hide the history sidebar. If 'initial' is True, only hide without toggling state label."""
        if self.history_visible:
            # remove from paned window
            try:
                self.main_container.forget(self.sidebar_frame)
            except Exception:
                pass
            self.history_visible = False
            if not initial:
                self.toggle_btn.config(text="☰")
        else:
            # determine size to use when showing
            desired_px = getattr(self, 'current_sidebar_width_px', self.min_sidebar_px)
            if hasattr(self, 'min_sidebar_px'):
                desired_px = max(desired_px, self.min_sidebar_px)
            # re-add to paned window on right side with appropriate minsize/width
            self.main_container.add(self.sidebar_frame, minsize=desired_px)
            try:
                self.main_container.paneconfigure(self.sidebar_frame, width=desired_px, stretch='never')
            except Exception:
                pass
            # also reposition sash
            try:
                total = self.root.winfo_width()
                self.main_container.sash_place(0, total - desired_px, 0)
            except Exception:
                pass

            self.history_visible = True
            if not initial:
                self.toggle_btn.config(text="×")
            # width already applied via paneconfigure
            try:
                self.main_container.update_idletasks()
            except Exception:
                pass


def run_app():
    """Launch the Symbolic Math Application."""
    root = tk.Tk()
    app = SymbolicMathApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
