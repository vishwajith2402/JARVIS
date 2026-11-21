import tkinter as tk

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Basic Calculator")
        self.geometry("400x400")

        self.result_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        entry = tk.Entry(self, textvariable=self.result_var, font=("Arial", 24), bd=10)
        entry.grid(row=0, column=0, columnspan=4)

        buttons = [
            ('7', 1, 0),
            ('8', 1, 1),
            ('9', 1, 2),
            ('/', 2, 0),
            ('4', 2, 1),
            ('5', 2, 2),
            ('*', 3, 0),
            ('1', 3, 1),
            ('2', 3, 2),
            ('-', 4, 0),
            ('0', 4, 1),
            ('.', 4, 2),
            ('+', 5, 0),
            ('3', 5, 1),
            ('=', 5, 2),
            ('=', 5, 2),
        ]

        for (text, row, col) in buttons:
            button = tk.Button(self, text=text, font=("Arial", 18), command=lambda t=text: self.on_button_click(t))
            button.grid(row=row, column=col)

    def on_button_click(self, button_text):
        if button_text == '=':
            try:
                result = eval(self.result_var.get())
                self.result_var.set(result)
            except:
                self.result_var.set("Error")
        else:
            self.result_var.set(self.result_var.get() + button_text)

if __name__ == "__main__":
    calculator = Calculator()
    calculator.mainloop()