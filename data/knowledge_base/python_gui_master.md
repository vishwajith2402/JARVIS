# Python GUI Development Master Guide (Tkinter)

## Core Principles
1. Use Python's built-in `tkinter` and `ttk` modules.
2. Structure applications using Object-Oriented Programming (`class App(tk.Tk)` or `class App:` with `root`).
3. Always separate business logic (calculations, algorithms) from GUI rendering.
4. Prevent GUI freezing: For long-running tasks, run the background work in a `threading.Thread(daemon=True)` and update GUI elements via `root.after()`.

## Template: Clean Modern Tkinter Window
```python
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class ModernApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TITAN Application")
        self.geometry("480x560")
        self.configure(bg="#0f172a")
        self.resizable(True, True)
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Label(self, text="TITAN Tool", font=("Segoe UI", 16, "bold"), fg="#38bdf8", bg="#0f172a")
        header.pack(pady=16)

        # Content Frame
        frame = tk.Frame(self, bg="#1e293b", padx=16, pady=16)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Input & Action Button
        self.entry = tk.Entry(frame, font=("Segoe UI", 12), bg="#334155", fg="#f8fafc", insertbackground="white")
        self.entry.pack(fill="x", pady=8)

        btn = tk.Button(frame, text="Execute Action", font=("Segoe UI", 11, "bold"), bg="#6366f1", fg="white", activebackground="#4f46e5", command=self.on_click)
        btn.pack(pady=12)

        # Output Text
        self.output = tk.Text(frame, height=8, font=("Consolas", 10), bg="#090d16", fg="#a5f3fc")
        self.output.pack(fill="both", expand=True, pady=6)

    def on_click(self):
        val = self.entry.get().strip()
        self.output.insert("end", f"Processed: {val}\n")

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
```

## Calculation & Expression Evaluator Safety
- When building calculators, sanitize mathematical expressions before calling `eval()` or use `ast.literal_eval`.
- Allowed characters: `0-9`, `+`, `-`, `*`, `/`, `.`, `(`, `)`.
