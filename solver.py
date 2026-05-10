import sympy as sp
import time

class EquationSolver:
    def __init__(self, equation_str):
        self.x = sp.Symbol('x')
        try:
            self.expr = sp.sympify(equation_str)
        except Exception as e:
            raise ValueError(f"Помилка вводу рівняння: {e}")

    def solve_bisection(self, a, b, tol, precision, max_iter=100):
        """Метод половинного ділення з логуванням кроків та часу."""
        start_time = time.perf_counter()
        a, b = float(a), float(b)
        fa = float(self.expr.subs(self.x, a).evalf())
        fb = float(self.expr.subs(self.x, b).evalf())

        if fa * fb > 0:
            raise ValueError("f(a) та f(b) повинні мати різні знаки.")

        log = []
        iter_count = 0

        for _ in range(max_iter):
            iter_count += 1
            c = (a + b) / 2.0
            fc = float(self.expr.subs(self.x, c).evalf())
            
            log.append(f"Крок {iter_count}: a={round(a, precision)}, b={round(b, precision)}, c={round(c, precision)}, f(c)={fc:.2e}")
            
            if abs(fc) < tol or (b - a) / 2.0 < tol:
                root = round(c, precision)
                break
            
            if fa * fc < 0:
                b = c
            else:
                a = c
                fa = fc
        else:
            root = round((a + b) / 2.0, precision)

        exec_time = time.perf_counter() - start_time
        return {"root": root, "iterations": iter_count, "time": exec_time, "log": log}

    def solve_newton(self, x0, tol, precision, max_iter=100):
        """Метод Ньютона з логуванням кроків та часу."""
        start_time = time.perf_counter()
        df = sp.diff(self.expr, self.x)
        x_n = complex(x0)
        
        log = []
        iter_count = 0

        for _ in range(max_iter):
            iter_count += 1
            fx_n = complex(self.expr.subs(self.x, x_n).evalf())
            dfx_n = complex(df.subs(self.x, x_n).evalf())
            
            if abs(dfx_n) < 1e-15:
                raise ValueError("Похідна занадто мала. Метод зупинено.")
            
            x_next = x_n - fx_n / dfx_n
            
            xn_str = f"{round(x_n.real, precision)}{'+' if x_n.imag >= 0 else ''}{round(x_n.imag, precision)}j"
            log.append(f"Крок {iter_count}: x_n = {xn_str}, f(x_n) = {fx_n.real:.2e}{'+' if fx_n.imag >= 0 else ''}{fx_n.imag:.2e}j")
            
            if abs(x_next - x_n) < tol:
                root = complex(round(x_next.real, precision), round(x_next.imag, precision))
                break
            x_n = x_next
        else:
            raise ValueError("Метод не зійшовся за задану кількість ітерацій.")

        exec_time = time.perf_counter() - start_time
        return {"root": root, "iterations": iter_count, "time": exec_time, "log": log}

    def solve_algebraic(self, precision):
        """Алгебраїчний метод. Не має ітерацій в класичному розумінні, але має час виконання."""
        start_time = time.perf_counter()
        roots = sp.solve(self.expr, self.x)
        
        complex_roots = []
        log = ["Символьне обчислення через SymPy..."]
        
        for r in roots:
            val = complex(r.evalf())
            complex_roots.append(complex(round(val.real, precision), round(val.imag, precision)))
            
        exec_time = time.perf_counter() - start_time
        return {"root": complex_roots, "iterations": 1, "time": exec_time, "log": log}

    def save_to_file(self, result_text, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result_text)