import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from solver import EquationSolver

class MathApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Розв'язувач рівнянь")
        self.resizable(False, False)
        self.last_result = ""
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack()

        ttk.Label(main_frame, text="Рівняння f(x) = 0 (напр. x**2 + 1):").grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.eq_entry = ttk.Entry(main_frame, width=50)
        self.eq_entry.insert(0, "x**4 + x**2 - 4")
        self.eq_entry.grid(row=1, column=0, columnspan=2, pady=5)

        settings_frame = ttk.LabelFrame(main_frame, text=" Параметри точності ", padding="5")
        settings_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.EW)

        ttk.Label(settings_frame, text="Епсилон (ε):").grid(row=0, column=0, padx=5)
        self.epsilon_entry = ttk.Entry(settings_frame, width=10)
        self.epsilon_entry.insert(0, "0.000001")
        self.epsilon_entry.grid(row=0, column=1, padx=5)

        ttk.Label(settings_frame, text="Знаків після коми:").grid(row=0, column=2, padx=5)
        self.prec_entry = ttk.Entry(settings_frame, width=5)
        self.prec_entry.insert(0, "4")
        self.prec_entry.grid(row=0, column=3, padx=5)

        ttk.Label(main_frame, text="Метод розв'язання:").grid(row=3, column=0, columnspan=2, sticky=tk.W)
        self.method_var = tk.StringVar(value="bisection")
        
        methods = [("Бісекція (дійсні)", "bisection"), ("Ньютона (комплексні)", "newton"), ("Алгебраїчний", "algebraic")]
        for i, (txt, val) in enumerate(methods):
            ttk.Radiobutton(main_frame, text=txt, value=val, variable=self.method_var, command=self.toggle_inputs).grid(row=4+i, column=0, columnspan=2, sticky=tk.W)

        self.params_frame = ttk.Frame(main_frame)
        self.params_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        self.lbl_a = ttk.Label(self.params_frame, text="a:")
        self.entry_a = ttk.Entry(self.params_frame, width=10)
        self.lbl_b = ttk.Label(self.params_frame, text="b:")
        self.entry_b = ttk.Entry(self.params_frame, width=10)
        self.lbl_x0 = ttk.Label(self.params_frame, text="x0 (напр. 1+1j):")
        self.entry_x0 = ttk.Entry(self.params_frame, width=15)

        self.btn_solve = ttk.Button(main_frame, text="Обчислити", command=self.solve)
        self.btn_solve.grid(row=8, column=0, columnspan=2, pady=5)
        
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=9, column=0, columnspan=2, pady=5)
        
        self.result_text = tk.Text(text_frame, height=10, width=55, state='disabled', background="#ffffff")
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH)
        
        scrollbar = ttk.Scrollbar(text_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        self.btn_save = ttk.Button(main_frame, text="Зберегти у файл", command=self.save_result, state='disabled')
        self.btn_save.grid(row=10, column=0, columnspan=2, pady=5)

        self.toggle_inputs()

    def toggle_inputs(self):
        for widget in self.params_frame.winfo_children():
            widget.grid_forget()
        method = self.method_var.get()
        if method == "bisection":
            self.lbl_a.grid(row=0, column=0)
            self.entry_a.grid(row=0, column=1, padx=5)
            self.entry_a.delete(0, tk.END)
            self.entry_a.insert(0, "1")
            self.lbl_b.grid(row=0, column=2)
            self.entry_b.grid(row=0, column=3, padx=5)
            self.entry_b.delete(0, tk.END)
            self.entry_b.insert(0, "2")
        elif method == "newton":
            self.lbl_x0.grid(row=0, column=0)
            self.entry_x0.grid(row=0, column=1, padx=5)
            self.entry_x0.delete(0, tk.END)
            self.entry_x0.insert(0, "1+0j")

    def validate_inputs(self):
        try:
            eps = float(self.epsilon_entry.get())
            if not (1e-18 <= eps <= 0.5):
                raise ValueError("Епсилон має бути в межах від 1e-18 до 0.5")
            
            prec = int(self.prec_entry.get())
            if not (0 <= prec <= 15):
                raise ValueError("Кількість знаків має бути від 0 до 15")
            
            return eps, prec
        except ValueError as e:
            messagebox.showerror("Помилка вводу", f"Некоректні параметри точності: {e}")
            return None, None

    def solve(self):
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.btn_save.config(state='disabled')
        
        eps, prec = self.validate_inputs()
        if eps is None: 
            self.result_text.config(state='disabled')
            return
        
        eq_str = self.eq_entry.get()
        method = self.method_var.get()
        
        try:
            solver = EquationSolver(eq_str)
            if method == "bisection":
                data = solver.solve_bisection(self.entry_a.get(), self.entry_b.get(), eps, prec)
                method_name = "Бісекція (дійсні)"
            elif method == "newton":
                data = solver.solve_newton(self.entry_x0.get().replace(' ', ''), eps, prec)
                method_name = "Ньютона (комплексні)"
            else:
                data = solver.solve_algebraic(prec)
                method_name = "Алгебраїчний"

            report = f"--- РЕЗУЛЬТАТИ ---"
            report += f"\nРівняння: {eq_str}"
            report += f"\nМетод: {method_name} (ε={eps})"
            report += f"\nЗнайдений корінь: {data['root']}"
            report += f"\n\n--- ПРАКТИЧНА ОЦІНКА СКЛАДНОСТІ ---"
            report += f"\nКількість ітерацій: {data['iterations']}"
            report += f"\nЧас виконання: {data['time'] * 1000:.4f} мілісекунд"
            report += f"\n\n--- ДЕМОНСТРАЦІЯ РОБОТИ ---"
            for step in data['log']:
                report += f"\n{step}"

            self.last_result = report
            self.result_text.insert(tk.END, self.last_result)
            self.btn_save.config(state='normal')

        except Exception as e:
            self.result_text.insert(tk.END, f"ПОМИЛКА ОБЧИСЛЕННЯ:\n{str(e)}")
            messagebox.showerror("Помилка", str(e))
        
        self.result_text.config(state='disabled')

    def save_result(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if path:
            EquationSolver("0").save_to_file(self.last_result, path)
            messagebox.showinfo("Успіх", "Результат збережено!")

if __name__ == "__main__":
    app = MathApp()
    app.mainloop()
