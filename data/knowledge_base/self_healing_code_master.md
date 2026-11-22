# Self-Healing Code & Autonomous Debugging Master Guide

## Core Principles
1. Catch errors early with `py_compile.compile(file, doraise=True)`.
2. Syntax Error Healing: Inspect the line number and token from `PyCompileError`, rewrite the exact line with valid syntax.
3. Tkinter Crash Prevention:
   - Never call `root.mainloop()` inside a secondary thread.
   - Always ensure widget variables (`StringVar`, `IntVar`) are created AFTER `root = Tk()`.
   - Use `row` and `column` with `.grid()` or `.pack()`, never mix `.grid()` and `.pack()` inside the same parent container.
4. NameError Prevention: Always ensure all imported names (`ttk`, `messagebox`, `math`, `os`, `sys`) are explicitly imported at the top of the file.
