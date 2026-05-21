import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from solver import EquationSolver

class MathApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Розв'язувач рівнянь")
        self.resizable(False, False)
        self.last_result = ""
        self.current_plot_data = None
        self.current_eq_str = ""
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack()

        ttk.Label(main_frame, text="Рівняння f(x) = 0:").grid(row=0, column=0, columnspan=2, sticky=tk.W)

        entry_frame = ttk.Frame(main_frame)
        entry_frame.grid(row=1, column=0, columnspan=2, pady=5)

        self.eq_entry = ttk.Entry(entry_frame, width=50)
        self.eq_entry.insert(0, "x**4 + x**2 - 4")
        self.eq_entry.pack(side=tk.LEFT)

        tk.Button(
            entry_frame,
            text="✕",
            relief=tk.GROOVE,
            font=("TkDefaultFont", 9),
            bg="#ffe0e0",
            activebackground="#ffb0b0",
            cursor="hand2",
            command=lambda: (self.eq_entry.delete(0, tk.END), self.eq_entry.focus()),
        ).pack(side=tk.LEFT, padx=(4, 0))

        kb_outer = ttk.Frame(main_frame)
        kb_outer.grid(row=2, column=0, columnspan=2, pady=(0, 4), sticky=tk.EW)

        buttons = [
            ("π",    "pi"),
            ("√x",   "sqrt(x)"),
            ("sin",  "sin("),
            ("cos",  "cos("),
            ("tan",  "tan("),
            ("cot",  "cot("),
            ("(",    "("),
            (")",    ")"),
            ("+",    "+"),
            ("−",    "-"),
            ("÷",    "/"),
            ("×",    "*"),
            ("**",   "**"),
        ]

        for col_idx, (label, insert_text) in enumerate(buttons):
            btn = tk.Button(
                kb_outer,
                text=label,
                width=4,
                relief=tk.GROOVE,
                font=("TkDefaultFont", 9),
                bg="#f0f0f0",
                activebackground="#d0e8ff",
                cursor="hand2",
                command=lambda t=insert_text: self.insert_symbol(t),
            )
            btn.grid(row=0, column=col_idx, padx=2, pady=1)

        settings_frame = ttk.LabelFrame(main_frame, text=" Параметри точності ", padding="5")
        settings_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.EW)

        ttk.Label(settings_frame, text="Епсилон (ε):").grid(row=0, column=0, padx=5)
        self.epsilon_entry = ttk.Entry(settings_frame, width=10)
        self.epsilon_entry.insert(0, "0.000001")
        self.epsilon_entry.grid(row=0, column=1, padx=5)

        ttk.Label(settings_frame, text="Знаків після коми:").grid(row=0, column=2, padx=5)
        self.prec_entry = ttk.Entry(settings_frame, width=5)
        self.prec_entry.insert(0, "4")
        self.prec_entry.grid(row=0, column=3, padx=5)

        ttk.Label(main_frame, text="Метод розв'язання:").grid(row=4, column=0, columnspan=2, sticky=tk.W)
        self.method_var = tk.StringVar(value="bisection")
        
        methods = [("Бісекція", "bisection"), ("Ньютона", "newton"), ("Алгебраїчний", "algebraic")]
        for i, (txt, val) in enumerate(methods):
            ttk.Radiobutton(main_frame, text=txt, value=val, variable=self.method_var, command=self.toggle_inputs).grid(row=5+i, column=0, columnspan=2, sticky=tk.W)

        self.params_frame = ttk.Frame(main_frame)
        self.params_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        self.lbl_a = ttk.Label(self.params_frame, text="a:")
        self.entry_a = ttk.Entry(self.params_frame, width=10)
        self.lbl_b = ttk.Label(self.params_frame, text="b:")
        self.entry_b = ttk.Entry(self.params_frame, width=10)
        self.lbl_x0 = ttk.Label(self.params_frame, text="x0 (напр. 1+1j):")
        self.entry_x0 = ttk.Entry(self.params_frame, width=15)

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=9, column=0, columnspan=2, pady=5)

        self.btn_solve = ttk.Button(buttons_frame, text="Обчислити", command=self.solve)
        self.btn_solve.pack(side=tk.LEFT, padx=5)

        self.btn_plot = ttk.Button(buttons_frame, text="Показати графік", command=self.show_plot, state='disabled')
        self.btn_plot.pack(side=tk.LEFT, padx=5)
        
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=10, column=0, columnspan=2, pady=5)
        
        self.result_text = tk.Text(text_frame, height=10, width=55, state='disabled', background="#ffffff")
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH)
        
        scrollbar = ttk.Scrollbar(text_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        self.btn_save = ttk.Button(main_frame, text="Зберегти у файл", command=self.save_result, state='disabled')
        self.btn_save.grid(row=11, column=0, columnspan=2, pady=5)

        self.toggle_inputs()

    def insert_symbol(self, text):
        try:
            pos = self.eq_entry.index(tk.INSERT)
        except Exception:
            pos = tk.END
        self.eq_entry.insert(pos, text)
        self.eq_entry.focus()
        try:
            self.eq_entry.icursor(int(pos) + len(text))
        except Exception:
            pass

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
            if not (1e-15 <= eps <= 0.5):
                raise ValueError("Епсилон має бути в межах від 1e-15 до 0.5")
            
            prec = int(self.prec_entry.get())
            if not (0 <= prec <= 15):
                raise ValueError("Кількість знаків має бути від 0 до 15")
            
            if self.method_var.get() == "bisection":
                a = float(self.entry_a.get())
                b = float(self.entry_b.get())
                if not (-1000000 <= a <= 1000000) or not (-1000000 <= b <= 1000000):
                    raise ValueError("Значення a та b мають бути в межах від -1000000 до 1000000")
                if a >= b:
                    raise ValueError("Значення a повинно бути меншим за b")
            
            return eps, prec
        except ValueError as e:
            messagebox.showerror("Помилка вводу", f"Некоректні параметри точності: {e}")
            return None, None

    def solve(self):
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.btn_save.config(state='disabled')
        self.btn_plot.config(state='disabled')
        self.current_plot_data = None
        
        eps, prec = self.validate_inputs()
        if eps is None: 
            self.result_text.config(state='disabled')
            return
        
        self.current_eq_str = self.eq_entry.get()
        method = self.method_var.get()
        
        try:
            solver = EquationSolver(self.current_eq_str)
            if method == "bisection":
                data = solver.solve_bisection(self.entry_a.get(), self.entry_b.get(), eps, prec)
                method_name = "Бісекція"
            elif method == "newton":
                data = solver.solve_newton(self.entry_x0.get().replace(' ', ''), eps, prec)
                method_name = "Ньютона"
            else:
                data = solver.solve_algebraic(prec)
                method_name = "Алгебраїчний"

            report = f"--- РЕЗУЛЬТАТИ ---"
            report += f"\nРівняння: {self.current_eq_str}"
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
            
            self.current_plot_data = data['plot_data']
            self.btn_plot.config(state='normal')

        except Exception as e:
            self.result_text.insert(tk.END, f"ПОМИЛКА ОБЧИСЛЕННЯ:\n{str(e)}")
            messagebox.showerror("Помилка", str(e))
        
        self.result_text.config(state='disabled')

    def show_plot(self):
        if not self.current_plot_data:
            return

        try:
            import numpy as np
            import matplotlib.pyplot as plt
            
            solver = EquationSolver(self.current_eq_str)
            
            root_val = self.current_plot_data.get('root', 0)
            
            is_complex = isinstance(root_val, complex) and abs(root_val.imag) > 1e-9
            
            if isinstance(root_val, list):
                real_xs = [r.real for r in root_val if abs(r.imag) <= 1e-9]
                if real_xs:
                    x_min, x_max = min(real_xs), max(real_xs)
                elif 'range' in self.current_plot_data:
                    x_min, x_max = self.current_plot_data['range']
                else:
                    x_min, x_max = -5, 5
            elif 'range' in self.current_plot_data:
                x_min, x_max = self.current_plot_data['range']
            else:
                ref_x = root_val.real if isinstance(root_val, complex) else root_val
                x_min, x_max = ref_x - 5, ref_x + 5
                
            padding = max(abs(x_max - x_min) * 0.2, 1.0)
            x_vals = np.linspace(x_min - padding, x_max + padding, 500)
            
            y_vals = []
            for val in x_vals:
                try:
                    y_res = float(solver.expr.subs(solver.x, float(val)).evalf())
                except:
                    y_res = np.nan
                y_vals.append(y_res)

            plt.rcParams['toolbar'] = 'None'

            plt.figure(num=f"Графік рівняння: {self.current_eq_str}", figsize=(8, 5))
            plt.plot(x_vals, y_vals, label=f"f(x) = {self.current_eq_str}", color='blue', linewidth=2)
            
            plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
            plt.axvline(0, color='black', linestyle='--', linewidth=0.8)
            
            if isinstance(root_val, list):
                real_roots = [r for r in root_val if abs(r.imag) <= 1e-9]
                complex_roots_only = [r for r in root_val if abs(r.imag) > 1e-9]

                for r in real_roots:
                    rx = r.real
                    try:
                        ry = float(solver.expr.subs(solver.x, float(rx)).evalf())
                    except:
                        ry = 0.0
                    plt.scatter([rx], [ry], color='red', s=100, zorder=5, label=f"Корінь: x ≈ {rx:.4f}")

                for r in complex_roots_only:
                    root_str = f"{round(r.real, 4)}{'+' if r.imag >= 0 else ''}{round(r.imag, 4)}j"
                    plt.plot([], [], ' ', label=f"Комплексний корінь:\nx = {root_str}\n(не відображається на 2D)")

            elif not is_complex:
                root_x = root_val.real if isinstance(root_val, complex) else root_val
                try:
                    root_y = float(solver.expr.subs(solver.x, float(root_x)).evalf())
                except:
                    root_y = 0.0

                plt.scatter([root_x], [root_y], color='red', s=100, zorder=5, label=f"Корінь: x ≈ {root_x:.4f}")
            else:
                root_str = f"{round(root_val.real, 4)}{'+' if root_val.imag >= 0 else ''}{round(root_val.imag, 4)}j"
                plt.plot([], [], ' ', label=f"Комплексний корінь:\nx = {root_str}\n(не відображається на 2D)")

            if self.method_var.get() == "bisection":
                plt.axvline(x_min, color='orange', linestyle=':', label='Границя a')
                plt.axvline(x_max, color='green', linestyle=':', label='Границя b')

            plt.title(f"Візуалізація функції f(x) = {self.current_eq_str}", fontsize=12)
            plt.xlabel("X")
            plt.ylabel("Y")
            plt.grid(True, which='both', linestyle=':', alpha=0.6)
            plt.legend()
            plt.show()

        except Exception as e:
            messagebox.showerror("Помилка побудови графіка", str(e))

    def save_result(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if path:
            EquationSolver("0").save_to_file(self.last_result, path)
            messagebox.showinfo("Успіх", "Результат збережено!")

if __name__ == "__main__":
    app = MathApp()
    app.mainloop()
