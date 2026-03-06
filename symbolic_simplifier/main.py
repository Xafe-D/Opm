"""
Main Entry Point for Symbolic Math Simplifier

Launches the GUI application for symbolic expression simplification.
Integrates the modular engine with the retro-styled user interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Import the core engine and utilities
from . import process
from .ui.interface import RetroButton, SymbolicMathApp

# For PDF export (requires reportlab package)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    _HAS_REPORTLAB = True
except ImportError:
    letter = None
    canvas = None
    _HAS_REPORTLAB = False


class SymbolicMathApp(tk.Widget):
    """Complete Symbolic Math Application with full UI.
    
    Provides a retro-styled interface for symbolic expression simplification
    with support for multiple export formats and a step-by-step solution trail.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("OPM - SYMBOLIC MATH GENERATOR v1.0")
        self.root.geometry("1000x750")
        self.root.configure(bg="#C0C080")
        self.monospace_font = ("Courier", 10)
        self.monospace_bold = ("Courier", 11, "bold")
        self.build_ui()

    def build_ui(self):
        # TITLE BANNER
        title_frame = tk.Frame(self.root, bg="#C0C080")
        title_frame.pack(fill="x", padx=5, pady=10)
        
        banner = tk.Label(
            title_frame,
            text="OPM - SYMBOLIC MATH CALCULATOR",
            font=("Courier", 14, "bold"),
            bg="#C0C080",
            fg="#000000",
            justify="center"
        )
        banner.pack()

        # INPUT PANEL
        input_frame = tk.Frame(self.root, bg="#C0C080", relief=tk.SUNKEN, bd=3)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(input_frame, text="Input Expression:", font=self.monospace_bold, bg="#C0C080", fg="#000000").pack(side="left", padx=8, pady=5)
        
        self.expression_entry = tk.Entry(
            input_frame,
            font=self.monospace_font,
            bg="#E8E8D0",
            fg="#000000",
            insertbackground="#000000",
            relief=tk.SUNKEN,
            bd=2
        )
        self.expression_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5, ipady=4)

        # BUTTON PANEL
        buttons_inner = tk.Frame(self.root, bg="#C0C080")
        buttons_inner.pack(pady=10)
        
        RetroButton(buttons_inner, "COMPUTE", command=self.compute_expression).pack(side="left", padx=5)
        RetroButton(buttons_inner, "CLEAR", command=self.clear_fields).pack(side="left", padx=5)
        RetroButton(buttons_inner, "COPY TRAIL", command=self.copy_trail).pack(side="left", padx=5)
        RetroButton(buttons_inner, "EXPORT", command=self.export_trail_prompt).pack(side="left", padx=5)

        # FINAL ANSWER PANEL
        final_frame = tk.Frame(self.root, bg="#C0C080", relief=tk.SUNKEN, bd=3)
        final_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(final_frame, text="Final Answer:", font=self.monospace_bold, bg="#C0C080", fg="#000000").pack(anchor="w", padx=8, pady=5)

        self.final_answer_label = tk.Label(
            final_frame,
            text="[Awaiting Input]",
            font=self.monospace_font,
            bg="#E8E8D0",
            fg="#000000",
            wraplength=900,
            justify="left",
            pady=8,
            padx=8,
            relief=tk.FLAT
        )
        self.final_answer_label.pack(fill="x", padx=5, pady=(0, 5))

        # SOLUTION TRAIL PANEL
        trail_frame = tk.Frame(self.root, bg="#C0C080", relief=tk.SUNKEN, bd=3)
        trail_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        tk.Label(trail_frame, text="Solution Trail:", font=self.monospace_bold, bg="#C0C080", fg="#000000").pack(anchor="w", padx=5, pady=3)

        trail_inner = tk.Frame(trail_frame, bg="#C0C080")
        trail_inner.pack(fill="both", expand=True, padx=3, pady=3)
        
        self.trail_text = tk.Text(
            trail_inner,
            wrap="word",
            font=self.monospace_font,
            bg="#E8E8D0",
            fg="#000000",
            insertbackground="#000000",
            relief=tk.SUNKEN,
            bd=2
        )
        self.trail_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(trail_inner, command=self.trail_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.trail_text.config(yscrollcommand=scrollbar.set, state="disabled")
        self.trail_text.tag_config("header", font=("Courier", 11, "bold"), foreground="#000000")
        self.trail_text.tag_config("section", foreground="#000000")

    def compute_expression(self):
        """Process the input expression and display results."""
        expr = self.expression_entry.get().strip()
        if not expr:
            messagebox.showwarning("INPUT ERROR", "[!] Please enter an expression.")
            return

        result = process(expr)
        self.trail_text.config(state="normal")
        self.trail_text.delete("1.0", tk.END)

        if result["status"] == "success":
            factored = result["final_answers"]["factored_form"]
            canonical = result["final_answers"]["canonical_form"]
            self.final_answer_label.config(
                text=f"✓ FACTORED: {factored}\n✓ CANONICAL: {canonical}"
            )

            badge_map = {
                "GIVEN": "[IN]",
                "METHOD": "[*]",
                "STEPS": "[->]",
                "FINAL ANSWER": "[!]",
                "VERIFICATION": "[OK]",
                "SUMMARY": "[#]"
            }

            sections = result["formatted_trail"].split("\n\n")
            for section in sections:
                if section.strip():
                    lines = section.strip().split("\n")
                    header_name = lines[0].upper()
                    badge = badge_map.get(header_name, "[?]")
                    header_text = f"{badge} {lines[0]}\n"
                    content_lines = lines[1:]

                    if header_name == "VERIFICATION":
                        for i, line in enumerate(content_lines):
                            if line.startswith("Status:"):
                                status = line.split(":")[1].strip()
                                icon = "[OK]" if status.lower() == "passed" else "[XX]"
                                content_lines[i] = f" {icon} {status}"

                    content_text = "\n".join(content_lines) + "\n\n"
                    self.trail_text.insert(tk.END, header_text, "header")
                    self.trail_text.insert(tk.END, content_text, "section")
        else:
            self.final_answer_label.config(text="[ERROR] Failed to compute")
            # show specific message if available
            err_msg = result.get("error_message") or "Failed to compute expression. Check syntax."
            messagebox.showerror("COMPUTATION ERROR", err_msg)

        self.trail_text.see("1.0")
        self.trail_text.config(state="disabled")

    def clear_fields(self):
        """Clear all input and output fields."""
        self.expression_entry.delete(0, tk.END)
        self.final_answer_label.config(text="[Awaiting Input]")
        self.trail_text.config(state="normal")
        self.trail_text.delete("1.0", tk.END)
        self.trail_text.config(state="disabled")

    def copy_trail(self):
        """Copy the simplification trail to clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.trail_text.get("1.0", tk.END))
        messagebox.showinfo("COPY STATUS", "[✓] Solution trail copied to clipboard!")

    def export_trail_prompt(self):
        """Ask user whether to export TXT or PDF"""
        trail_content = self.trail_text.get("1.0", tk.END).strip()
        if not trail_content:
            messagebox.showwarning("EXPORT ERROR", "[!] Nothing to export. Compute an expression first.")
            return

        if _HAS_REPORTLAB:
            choice = messagebox.askquestion("EXPORT FORMAT", "[?] Export as PDF?\n[YES] PDF  |  [NO] TXT")
            if choice == "yes":
                self.export_pdf(trail_content)
            else:
                self.export_txt(trail_content)
        else:
            messagebox.showwarning("MISSING DEPENDENCY", 
                                   "[!] PDF export requires the 'reportlab' package.\n"
                                   "Install it via pip and restart the application.")
            self.export_txt(trail_content)

    def export_txt(self, content):
        """Export simplification trail as text file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                                                 title="[SAVE] Solution Trail As")
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("EXPORT SUCCESSFUL", f"[✓] Solution trail saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("EXPORT FAILED", f"[!] Could not save file:\n{str(e)}")

    def export_pdf(self, content):
        """Export simplification trail as PDF file."""
        if not _HAS_REPORTLAB:
            messagebox.showerror("EXPORT FAILED", "[!] ReportLab is not available; cannot create PDF.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
                                                 title="[SAVE] Solution Trail As PDF")
        if file_path:
            try:
                c = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter
                y = height - 40
                for line in content.split("\n"):
                    if any(line.startswith(badge) for badge in ["[IN]", "[*]", "[→]", "[!]", "[✓]", "[#]"]):
                        c.setFont("Courier-Bold", 12)
                        c.setFillColorRGB(0, 0.5, 0)  # green
                    else:
                        c.setFont("Courier", 10)
                        c.setFillColorRGB(0, 0, 0)
                    c.drawString(40, y, line)
                    y -= 14
                    if y < 40:
                        c.showPage()
                        y = height - 40
                c.save()
                messagebox.showinfo("EXPORT SUCCESSFUL", f"[✓] Solution trail saved as PDF:\n{file_path}")
            except Exception as e:
                messagebox.showerror("EXPORT FAILED", f"[!] Could not save PDF:\n{str(e)}")


def run_app():
    """Launch the Symbolic Math Application."""
    root = tk.Tk()
    app = SymbolicMathApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
