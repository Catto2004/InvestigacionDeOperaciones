# optimizer.py
# Implementación del Optimizer con Simplex, Dual y Dual Simplex

import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import time

console = Console()

class Optimizer:
    def __init__(self, objective_function, constraints, objetivo, verbose=True):
        """
        objective_function: dict {'x1':3, 'x2':2} (parse_objective_function)
        constraints: list of tuples [( {'x1':1,'x2':2}, '<=', 10 ), ...] (parse_constraints)
        objetivo: 'max' or 'min'
        verbose: imprime mensajes y tablas (usa Rich)
        """
        self.obj_func = objective_function
        self.constraints = constraints
        self.objetivo = objetivo.lower()
        self.verbose = verbose
        self.var_names = None

    def _parse_problem(self):
        # Obtener todas las variables presentes en el problema
        vars_order = sorted(list(set(var for expr, _, _ in self.constraints for var in expr.keys())))
        self.var_names = vars_order
        n = len(vars_order)

        # Construir matrices A y b
        A = []
        b = []

        for expr, sign, rhs in self.constraints:
            row = [expr.get(v, 0.0) for v in vars_order]
            # Normalizar todas las restricciones al formato <= (agregando signo negativo si es necesario)
            if sign == '>=':
                row = [-a for a in row]
                rhs = -rhs
            elif sign == '=':
                # Duplicamos la ecuación como <= y >=
                A.append(row)
                b.append(rhs)
                row = [-a for a in row]
                rhs = -rhs
            A.append(row)
            b.append(rhs)

        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)

        # Vector de coeficientes de la función objetivo (ordenado)
        c = np.array([self.obj_func.get(v, 0.0) for v in vars_order], dtype=float)

        return A, b, c

    # --------------------- Interfaz pública ---------------------
    def solve_dual(self):
        if self.verbose:
            console.print(Panel.fit("[bold cyan]FORMULACIÓN DEL PROBLEMA DUAL[/bold cyan]", title="Dual", style="blue"))

        try:
            A, b, c = self._parse_problem()
            dual = self._build_dual_representation()

            obj_type = "Maximizar" if dual['obj_type'] == 'max' else "Minimizar"
            terms = [f"{self._format_num(coef)}{var}" for coef, var in zip(dual['obj_coeffs'], dual['var_names'])]
            console.print(f"[bold]{obj_type} W =[/bold] " + " + ".join(terms))

            console.print("\n[bold]Sujeto a:[/bold]")
            for i, (coef_list, sign, rhs) in enumerate(dual['constraints']):
                expr = []
                for coef, y in zip(coef_list, dual['var_names']):
                    if abs(coef - 1) < 1e-9:
                        expr.append(f"{y}")
                    elif abs(coef + 1) < 1e-9:
                        expr.append(f"-{y}")
                    else:
                        expr.append(f"{self._format_num(coef)}{y}")
                console.print(f"  {' + '.join(expr)} {sign} {self._format_num(rhs)}")

            console.print("\n[bold]Signos de variables duales:[/bold]")
            for name, sign in zip(dual['var_names'], dual['var_signs']):
                console.print(f"  {name} {sign}")

            return None, None, "Se mostró la formulación del problema dual. No se resolvió numéricamente."

        except Exception as e:
            console.print(f"[red]Error en solve_dual: {e}[/red]")
            return None, None, f"Error en solve_dual: {e}"


    # --------------------- Método Simplex primal ---------------------
    def solve_simplex(self):
        if self.verbose:
            console.print(Panel.fit("[bold cyan]EJECUCIÓN: SIMPLEX PRIMAL[/bold cyan]", style="green"))

        try:
            start = time.time()
            A, b, c = self._parse_problem()
            if np.any(b < 0):
                console.print("[yellow]RHS contiene valores negativos -> conviene usar Dual Simplex o introducir artificiales.[/yellow]")
                return self.solve_dual()

            if self.objetivo == 'min':
                c = -c  # Convertimos el problema a maximización

            tableau = self._create_tableau_for_primal(A, b, c)
            result = self._primal_simplex(tableau, c, A, b)
            if result is None:
                return None
            x, z, status = result  # z ya está correcto

            # Mostrar resultados
            if self.verbose:
                console.print(Panel(f"[bold green]{status}[/bold green]\n\n[bold]Valor objetivo:[/bold] {self._format_num(z)}", title="Resultados", style="magenta"))
                var_names = [f"x{i+1}" for i in range(len(x))]  # x1, x2, x3...
                rows = "\n".join([f"  [bold]{name}[/bold] = {self._format_num(val)}" for name, val in zip(var_names, x)])
                console.print(rows)
                console.print(f"\n⏱️ Tiempo total Simplex: {time.time() - start:.4f} s", style="dim")

            return x, z, status

        except Exception as e:
            console.print(f"[red]Error en solve_simplex: {e}[/red]")
            return None


    # --------------------- Impresión / utilidades ---------------------
    def _format_num(self, v):
        """Formato limpio para coeficientes (quita .0 innecesarios)."""
        try:
            vv = float(v)
        except:
            return str(v)
        if abs(vv - int(vv)) < 1e-9:
            return str(int(round(vv)))
        # limitar a 4 decimales visibles, sin ceros finales
        return f"{vv:.4f}".rstrip('0').rstrip('.')

    def _build_primal_representation(self):
        """
        Construye una representación imprimible del problema primal
        a partir de self.constraints y self.obj_func.
        """
        # ordenar variables en un orden consistente
        vars_order = sorted(list(set(var for expr, _, _ in self.constraints for var in expr.keys())))
        self.var_names = vars_order
        n = len(vars_order)

        # construir A, b y constraints legibles
        constraints_repr = []
        for expr, sign, rhs in self.constraints:
            row = [expr.get(v, 0) for v in vars_order]
            constraints_repr.append((row, sign, rhs))

        # obj coeffs aligned with var order
        obj_coeffs = [self.obj_func.get(v, 0) for v in vars_order]
        var_signs = ['>= 0' for _ in vars_order]  # asumimos no-negatividad por defecto

        return {
            'obj_type': self.objetivo,
            'obj_coeffs': obj_coeffs,
            'var_names': vars_order,
            'var_signs': var_signs,
            'constraints': constraints_repr
        }

    def _build_dual_representation(self):
        """
        Construye la representación (texto + datos) del problema dual
        a partir de self.constraints y self.obj_func.
        """
        # Obtener orden consistente de variables primal
        vars_order = sorted(list(set(var for expr, _, _ in self.constraints for var in expr.keys())))
        m = len(self.constraints)
        n = len(vars_order)

        # Reconstruir A_original, b_orig y signos originales (sin normalizar)
        A_orig = []
        b_orig = []
        sign_list = []
        for expr, sign, rhs in self.constraints:
            row = [expr.get(v, 0) for v in vars_order]
            A_orig.append(row)
            b_orig.append(rhs)
            sign_list.append(sign.strip())

        # Determinar tipo objetivo dual
        dual_obj_type = 'min' if self.objetivo == 'max' else 'max'
        dual_obj_coeffs = b_orig  # b's become objective coeffs in dual
        dual_constraints = []

        # Para cada variable primal j construimos restricción dual
        for j in range(n):
            coeffs = [A_orig[i][j] for i in range(m)]
            sign = '>=' if self.objetivo == 'max' else '<='
            rhs = float(self.obj_func.get(vars_order[j], 0))
            dual_constraints.append((coeffs, sign, rhs))

        # Signos de variables duales según restricción primal correspondiente
        var_signs = []
        for s in sign_list:
            if s == '<=':
                var_signs.append('>= 0')
            elif s == '>=':
                var_signs.append('<= 0')
            else:
                var_signs.append('libre')

        var_names = [f"y{i+1}" for i in range(m)]

        return {
            'obj_type': dual_obj_type,
            'obj_coeffs': dual_obj_coeffs,
            'var_names': var_names,
            'var_signs': var_signs,
            'constraints': dual_constraints
        }

    # --------------------- Creación de tableau ---------------------
    def _create_tableau_for_primal(self, A, b, c):
        m, n = A.shape
        tableau = np.zeros((m + 1, n + m + 1))
        tableau[:m, :n] = A
        tableau[:m, n:n + m] = np.eye(m)
        tableau[:m, -1] = b
        tableau[-1, :n] = -c
        tableau[-1, -1] = 0.0
        return tableau

    def _create_tableau_for_dual(self, A, b, c):
        # Simétrica a _create_tableau_for_primal, con -c en fila objetivo.
        m, n = A.shape
        tableau = np.zeros((m + 1, n + m + 1))
        tableau[:m, :n] = A
        tableau[:m, n:n + m] = np.eye(m)
        tableau[:m, -1] = b
        tableau[-1, :n] = -c
        tableau[-1, -1] = 0.0
        return tableau


    # --------------------- Simplex primal (implementación) ---------------------
    def _primal_simplex(self, tableau, c, A, b, max_iters=200):
        """
        tableau: array (m+1) x (n+m+1) donde m = #restricciones, n = #variables
        """
        rows, total_cols = tableau.shape
        num_constraints = rows - 1
        n = A.shape[1]
        iter_count = 0

        # Variables básicas iniciales (asumimos las de holgura)
        basic_vars = [f"s{i+1}" for i in range(num_constraints)]

        if self.verbose:
            console.print("\n[bold]Iteraciones del Simplex Primal[/bold]\n")

        while True:
            iter_count += 1
            if self.verbose:
                console.print(f"\n[bold]--- Iteración {iter_count} ---[/bold]")

                # Mostrar tabla con columna de variables básicas
                headers = ["Base"] + [f"x{i+1}" for i in range(n)] + [f"s{i+1}" for i in range(num_constraints)] + ["RHS"]
                table = Table(box=box.MINIMAL_DOUBLE_HEAD, show_edge=True)
                for h in headers:
                    table.add_column(h, justify="center", style="white")

                # filas de restricciones
                for i in range(num_constraints):
                    row_vals = [self._format_num(v) for v in tableau[i, :n + num_constraints + 1]]
                    table.add_row(basic_vars[i], *row_vals)

                # fila objetivo
                obj_vals = [self._format_num(v) for v in tableau[-1, :n + num_constraints + 1]]
                table.add_row("Z", *obj_vals)

                console.print(table)

            # Fila objetivo (última, sin RHS)
            obj_row = tableau[-1, :-1]
            j = int(np.argmin(obj_row))  # columna con coeficiente más negativo

            # Criterio de optimalidad
            if tableau[-1, j] >= -1e-9:
                if self.verbose:
                    console.print("[green]Y Óptimo alcanzado (fila objetivo no tiene coeficientes negativos).[/green]")
                break

            # Calcular razones
            ratios = np.full(num_constraints, np.inf)
            for i in range(num_constraints):
                aij = tableau[i, j]
                if aij > 1e-12:
                    ratios[i] = tableau[i, -1] / aij

            if np.all(np.isinf(ratios)):
                console.print("[red]!!! Problema no acotado (Simplex primal).[/red]")
                return None

            # Fila pivote
            i = int(np.argmin(ratios))
            pivot = tableau[i, j]

            entering = f"x{j+1}" if j < n else f"s{j-n+1}"
            leaving = basic_vars[i]

            if self.verbose:
                console.print(f"Pivote elegido → Fila: {i+1}, Columna: {j+1} ({entering}), Valor: {self._format_num(pivot)}")
                console.print(f"Entra: [bold green]{entering}[/bold green], Sale: [bold yellow]{leaving}[/bold yellow]")

            # Pivoteo
            tableau[i, :] = tableau[i, :] / pivot
            for r in range(rows):
                if r != i:
                    tableau[r, :] -= tableau[r, j] * tableau[i, :]

            # Actualizar variable básica
            basic_vars[i] = entering

            if iter_count >= max_iters:
                console.print("[yellow]! Se alcanzó el máximo de iteraciones (Simplex primal).[/yellow]")
                break

        # Construir solución
        x = np.zeros(n)
        for idx, vb in enumerate(basic_vars):
            if vb.startswith("x"):
                xi = int(vb[1:]) - 1
                if 0 <= xi < n:
                    x[xi] = tableau[idx, -1]

        z = tableau[-1, -1]

        # Verificación de factibilidad
        Ax = np.dot(A, x)
        if self.verbose:
            if np.all(Ax <= b + 1e-6):
                console.print("\n[green]Y Solución factible verificada (primal).[/green]")
            else:
                console.print("\n[yellow]! Solución primal NO cumple todas las restricciones.[/yellow]")
            console.print(f"[dim]Variables básicas: {basic_vars}[/dim]")

        return x, z, "Óptimo alcanzado (Simplex primal)"


    # --------------------- Dual Simplex ---------------------
    def _dual_simplex(self, tableau, c, A, b, show_table=True, max_iters=200):
        """
        Implementación del Dual Simplex con visualización Rich.
        tableau: (m+1) x (n+m+1) (m = #restricciones, n = #variables)
        """
        rows, total_cols = tableau.shape
        num_constraints = rows - 1
        n = A.shape[1]
        iteracion = 0

        # Nombres de columnas y variables básicas
        col_names = [f"x{i+1}" for i in range(n)] + [f"s{j+1}" for j in range(num_constraints)]
        basic_vars = [f"s{i+1}" for i in range(num_constraints)]

        if self.verbose and show_table:
            console.print("\n[bold]Iteraciones del método Dual Simplex:[/bold]\n")

        while True:
            iteracion += 1
            if self.verbose and show_table:
                console.print(f"\n[bold]--- Iteración {iteracion} ---[/bold]")

                table = Table(box=box.MINIMAL_DOUBLE_HEAD)
                headers = ["VB"] + col_names + ["RHS"]
                for h in headers:
                    table.add_column(h, justify="center")

                # filas de restricciones
                for i in range(num_constraints):
                    row_vals = [self._format_num(v) for v in tableau[i, :n + num_constraints + 1]]
                    table.add_row(basic_vars[i], *row_vals)
                # fila objetivo
                obj_vals = [self._format_num(v) for v in tableau[-1, :n + num_constraints + 1]]
                table.add_row("Z", *obj_vals)

                console.print(table)

            # Fila con RHS más negativo → fila pivote
            row_pivot = int(np.argmin(tableau[:-1, -1]))
            if tableau[row_pivot, -1] >= -1e-9:
                if self.verbose:
                    console.print("\n[green]Y Óptimo alcanzado (RHS no negativo).[/green]")
                break

            # Selección de columna pivote (mínimo ratio z_j / a_ij para a_ij < 0)
            ratios = []
            for j in range(total_cols - 1):
                aij = tableau[row_pivot, j]
                if aij < -1e-12:
                    ratios.append(tableau[-1, j] / aij)
                else:
                    ratios.append(np.inf)

            if all(np.isinf(ratios)):
                console.print("[red]!!! Problema infactible (Dual Simplex).[/red]")
                return None

            col_pivot = int(np.argmin(ratios))
            pivot = tableau[row_pivot, col_pivot]

            entering = col_names[col_pivot]
            leaving = basic_vars[row_pivot]

            if self.verbose:
                console.print(f"Iteración {iteracion}: Entra -> [green]{entering}[/green] ; Sale -> [yellow]{leaving}[/yellow] ; "
                    f"Pivote en ({row_pivot+1}, {col_pivot+1}) = {self._format_num(pivot)}")

            if abs(pivot) < 1e-12:
                console.print("[red]!!! Pivot nulo detectado, abortando para evitar división por cero.[/red]")
                return None

            # Operaciones de pivoteo
            tableau[row_pivot, :] /= pivot
            for r in range(rows):
                if r != row_pivot:
                    tableau[r, :] -= tableau[r, col_pivot] * tableau[row_pivot, :]

            # Actualizar variables básicas
            basic_vars[row_pivot] = entering

            if iteracion >= max_iters:
                console.print("[yellow]! Se alcanzó el máximo de iteraciones (Dual Simplex).[/yellow]")
                break

        # === RESULTADOS FINALES ===
        x = np.zeros(n)
        s = np.zeros(num_constraints)

        for i, vb in enumerate(basic_vars):
            if vb.startswith("x"):
                idx = int(vb[1:]) - 1
                if 0 <= idx < n:
                    x[idx] = tableau[i, -1]
            elif vb.startswith("s"):
                idx = int(vb[1:]) - 1
                if 0 <= idx < num_constraints:
                    s[idx] = tableau[i, -1]

        # Calcular valor objetivo directamente
        c_original = np.array([self.obj_func.get(f"x{i+1}", 0.0) for i in range(n)], dtype=float)
        z = float(np.dot(c_original, x))

        Ax = np.dot(A, x)

        console.print(Panel.fit("[bold cyan]RESULTADOS FINALES (Dual Simplex)[/bold cyan]", style="blue"))
        for i, val in enumerate(x, start=1):
            console.print(f"x{i} = {self._format_num(val)}")
        for i, val in enumerate(s, start=1):
            console.print(f"s{i} = {self._format_num(val)}")
        console.print(f"\nZ = {self._format_num(z)}")

        # Verifica según el signo del término independiente (b)
        if np.allclose(Ax, b, atol=1e-6) or np.all(Ax >= b - 1e-6) or np.all(Ax <= b + 1e-6):
            console.print("\n[green]Y Solución factible verificada (dual).[/green]")
        else:
            console.print("\n[yellow]! Solución dual NO cumple todas las restricciones (verificación general).[/yellow]")

        return x, z, "Óptimo alcanzado (Dual Simplex)"
