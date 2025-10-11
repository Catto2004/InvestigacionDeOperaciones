# Simplex/SimplexSolver.py
# Simplex paso-a-paso con soporte básico de Two-Phase (artificiales).
# Usa Parser.Parsear para leer la FO y restricciones.

import numpy as np
from Parser import Parsear

EPS = 1e-9

class SimplexSolver:
    """
    Solver interactivo paso-a-paso.
    Uso:
        <p>solver = SimplexSolver()<br/>
        solver.initialize(modo, funcion_objetivo_str, restricciones_list)<br/>
        while not solver.is_optimal():<br/>
            info = solver.iterate_one()<br/>
            # info contiene meta de la iteración y snapshot para mostrar<p/>
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.modo = "Max"
        self.var_names = []     # nombres de variables (x1,x2, s1, a1, ...)
        self.A = None           # matriz m x n_total
        self.b = None           # vector m
        self.c = None           # vector n_total (para FO original, ceros para slacks/artifs)
        self.tipos = []         # operadores originales de restricciones
        self.basis = []         # índices de variables básicas (longitud m)
        self.iteration = 0
        self.phase = 2          # 1 si en fase I, 2 en fase II
        self.artificials = []   # índices de variables artificiales
        self.status_flag = "initialized"  # "ok","optimal","unbounded","infeasible"
        self.history = []       # lista de dicts con cada iteración


    # ################ Inicialización y construcción del modelo ################
    def initialize(self, modo: str, funcion_objetivo: str, restricciones: list[str]):
        """
        Recibe: modo ("Max" o "Min"), funcion_objetivo como string, lista de restricciones string.
        Construye la forma estándar añadiendo slack/surplus/artificials y prepara Phase I si es necesario.
        """
        self.reset()
        self.modo = modo if modo in ("Max", "Min") else "Max"

        # permitir función objetivo sin operador (p.ej. "3x1 + 5x2")
        if not any(op in funcion_objetivo for op in ("<=", ">=", "=")):
            parsed_fo = Parsear(funcion_objetivo + " <= 0")
        else:
            parsed_fo = Parsear(funcion_objetivo)
        # Parsear restricciones
        parsed_constraints = [Parsear(r) for r in restricciones]

        # Determinar n_vars original (máximo índice)
        max_idx = parsed_fo.get("max_var", -1)
        for p in parsed_constraints:
            if p.get("max_var", -1) > max_idx:
                max_idx = p["max_var"]
        if max_idx < 0:
            raise ValueError("No se detectaron variables en la entrada.")

        n_orig = max_idx + 1
        c_orig = parsed_fo["coef"][:n_orig]

        # Construcción incremental de A, c y nombres de variables
        A_rows = []
        b = []
        tipos = []
        var_names = [f"x{i+1}" for i in range(n_orig)]
        c = list(c_orig)  # empezamos con coef de variables originales

        basis = []
        artificials = []
        # Contadores para slacks/surplus/artificials
        s_count = 0
        a_count = 0

        # Procesar cada restricción y añadir columnas según tipo
        for ridx, p in enumerate(parsed_constraints):
            row = p["coef"][:n_orig]  # fila base para variables originales
            oper = p["operador"]
            rhs = p["constante"]

            # Si es <= : añadimos slack +1 y lo ponemos en base
            if oper == "<=":
                # slack
                s_count += 1
                row.extend([1.0])   # columna del slack
                var_names.append(f"s{s_count}")
                c.append(0.0)
                basis.append(len(c) - 1)  # slack en base
            elif oper == ">=":
                # surplus (-1) y artificial (+1)
                s_count += 1
                # columna de surplus
                row.extend([-1.0])
                var_names.append(f"r{s_count}")  # surplus
                c.append(0.0)
                # artificial
                a_count += 1
                row.extend([1.0])
                var_names.append(f"a{a_count}")
                c.append(0.0)
                artificials.append(len(c) - 1)
                basis.append(len(c) - 1)  # artificial en base
            elif oper == "=" or oper is None:
                # igualdad -> artificial
                a_count += 1
                row.extend([1.0])
                var_names.append(f"a{a_count}")
                c.append(0.0)
                artificials.append(len(c) - 1)
                basis.append(len(c) - 1)
            else:
                raise ValueError(f"Operador no soportado en restricción: {oper}")

            # Rellenar las columnas que ya existían para filas anteriores:
            # Si la fila es más corta que otras por nuevas columnas, las extendemos
            # (se hace después de construir todas filas)
            A_rows.append(row)
            b.append(rhs)
            tipos.append(oper)

        # Ahora normalizamos la longitud de todas las filas y c
        n_total = len(c)
        # A_rows pueden tener longitudes diferentes (cada fila había extendido columnas en su momento)
        for i in range(len(A_rows)):
            if len(A_rows[i]) < n_total:
                A_rows[i].extend([0.0] * (n_total - len(A_rows[i])))

        # Guardar en el solver
        self.var_names = var_names
        self.A = np.array(A_rows, dtype=float)
        self.b = np.array(b, dtype=float)
        # Para la c original: si modo == "Min" convertimos a Max internamente (c = -c)
        if self.modo == "Min":
            self.c = np.array([-float(v) for v in c], dtype=float)
        else:
            self.c = np.array(c, dtype=float)

        self.tipos = tipos
        self.basis = basis.copy()
        self.artificials = artificials.copy()
        self.iteration = 0

        # Si hay artificiales -> arrancar en fase I
        if len(self.artificials) > 0:
            self.phase = 1
            # Construir vector c_phase1: minimizar suma de artificiales.
            # Asumime que la fase I es minimización; como internamente trabaja con c para Max,
            # Pone +1 en el coste de las artificiales y 0 en el resto (usaremos lógica de signs en reduced costs).
            self.c_phase1 = np.zeros(len(self.c), dtype=float)
            for aidx in self.artificials:
                if 0 <= aidx < len(self.c_phase1):
                    self.c_phase1[aidx] = 1.0
        else:
            self.phase = 2
            self.c_phase1 = None

        self.status_flag = "ready"


    # ################ Cálculos internos ################
    def _get_B_and_N(self):
        """Retorna B (m x m), N (m x n_no_básicas), índices no básicas."""
        m = self.A.shape[0]
        Bcols = [ self.A[:, j] for j in self.basis ]
        B = np.column_stack(Bcols) if len(Bcols) > 0 else np.zeros((m,0))
        nonbas = [j for j in range(self.A.shape[1]) if j not in self.basis]
        N = self.A[:, nonbas] if len(nonbas) > 0 else np.zeros((self.A.shape[0], 0))
        return B, N, nonbas

    def _compute_current_solution(self):
        B, N, nonbas = self._get_B_and_N()
        if B.size == 0:
            xB = np.zeros(0)
            B_inv = np.zeros((self.A.shape[0], self.A.shape[0]))
        else:
            try:
                B_inv = np.linalg.inv(B)
            except np.linalg.LinAlgError:
                # alternativa: usar solve por columna
                B_inv = np.linalg.pinv(B)
            xB = B_inv.dot(self.b)
        # Calcular Z = c_B^T * xB
        cB = np.array([ self.c[j] for j in self.basis ]) if len(self.basis)>0 else np.zeros(0)
        Z = float(cB.dot(xB)) if xB.size>0 else 0.0
        return xB, Z, B_inv

    def _reduced_costs(self, B_inv, c_vector=None):
        """Calcula costos reducidos r_j = c_j - c_B^T * B_inv * A[:,j]
        c_vector: si se pasa, se usa ese vector de costes (útil para fase I).
        """
        if c_vector is None:
            c_vector = self.c
        m = self.A.shape[0]
        n = self.A.shape[1]
        cB = np.array([ c_vector[j] for j in self.basis ]) if len(self.basis)>0 else np.zeros(0)
        yT = cB.dot(B_inv) if B_inv is not None and cB.size>0 else np.zeros((m,))
        r = np.zeros(n)
        for j in range(n):
            if j in self.basis:
                r[j] = 0.0
            else:
                a_j = self.A[:, j]
                r[j] = c_vector[j] - yT.dot(a_j)
        return r


    # ################ Decisión de variable entrante y saliente ################
    def _choose_entering(self, r):
        """Devuelve índice de variable entrante o None si óptimo.
           - Si self.phase == 1: objetivo es MINIMIZAR suma de artificiales -> elegir r_j < -EPS (para minim)
           - Si self.phase == 2: objetivo original que lo convertimos a maximización en c
        """
        n = len(r)
        indices = [j for j in range(n) if j not in self.basis]
        if self.phase == 1:
            # En fase I buscamos disminuir suma de artificiales (minimización).
            # Seleccionamos una variable con costo reducido < -EPS (indicando que al bajar la FO de fase1 mejora).
            candidates = [j for j in indices if r[j] < -EPS]
            if not candidates:
                return None
            return min(candidates)  # Regla de Bland: menor índice
        else:
            # Fase II: objetivo convertido a maximización (c preparado en initialize)
            candidates = [j for j in indices if r[j] > EPS]
            if not candidates:
                return None
            return min(candidates)  # Desempate de Bland
        
    def _choose_leaving(self, B_inv, entering, xB):
        a_j = self.A[:, entering]
        d = B_inv.dot(a_j)
        ratios = []
        for i, val in enumerate(d):
            if val > EPS:
                ratios.append((xB[i] / val, i))
        if not ratios:
            return None, None
        min_ratio, row = min(ratios, key=lambda x: (x[0], self.basis[x[1]]))
        return row, self.basis[row]


    # ################ Iteración única (pivote) ################
    def iterate_one(self):
        """
        Ejecuta un paso de simplex (una pivotación).
        Devuelve dict con info: {
            'iteration': k,
            'entering': idx o None,
            'leaving': idx o None,
            'status': 'optimal'|'continue'|'unbounded'|'infeasible'|'phase1_to_phase2',
            'tableau_snapshot': snapshot (lista de filas con nombres y valores),
            'Z': valor,
        }
        """
        if self.status_flag in ("optimal","unbounded","infeasible"):
            return {"status": self.status_flag}

        m = self.A.shape[0]
        # 1) Calcular B_inv y solución actual
        B, N, nonbas = self._get_B_and_N()
        if B.size == 0:
            B_inv = np.zeros((m, m))
        else:
            try:
                B_inv = np.linalg.inv(B)
            except np.linalg.LinAlgError:
                B_inv = np.linalg.pinv(B)

        xB, Z, _ = self._compute_current_solution()

        # 2) Calcular costos reducidos según fase
        if self.phase == 1 and self.c_phase1 is not None:
            r = self._reduced_costs(B_inv, c_vector=self.c_phase1)
        else:
            r = self._reduced_costs(B_inv, c_vector=self.c)

        # Fase I: ver si terminó la fase I
        if self.phase == 1:
            # calcular valor objetivo fase1 = suma de valores de artificiales en la base
            art_vals = [ xB[i] for i,bidx in enumerate(self.basis) if bidx in self.artificials ]
            phase1_obj = sum(art_vals) if len(art_vals)>0 else 0.0

            entering = self._choose_entering(r)
            if entering is None:
                # terminó fase 1
                if phase1_obj > 1e-6:
                    self.status_flag = "infeasible"
                    return {"status": "infeasible", "phase1_obj": phase1_obj}
                # eliminar artificials y pasar a fase 2
                try:
                    self._remove_artificials()
                except RuntimeError as e:
                    self.status_flag = "infeasible"
                    return {"status": "infeasible", "error": str(e)}
                self.phase = 2
                # recalc y devolver snapshot de cambio de fase
                B, N, nonbas = self._get_B_and_N()
                try:
                    B_inv = np.linalg.inv(B)
                except np.linalg.LinAlgError:
                    B_inv = np.linalg.pinv(B)
                xB, Z, _ = self._compute_current_solution()
                r = self._reduced_costs(B_inv, c_vector=self.c)
                self.iteration += 1
                return {
                    "status": "phase1_to_phase2",
                    "phase1_obj": phase1_obj,
                    "iteration": self.iteration,
                    "Z": Z,
                    "snapshot": self.get_tableau_display()
                }
            # si hay entering en fase1, seguimos a pivoteo de fase1 (usa r calculado arriba)

        # Fase II normal: seleccionar entrante
        entering = self._choose_entering(r)
        if entering is None:
            self.status_flag = "optimal"
            return {"status": "optimal", "iteration": self.iteration, "Z": Z, "snapshot": self.get_tableau_display()}

        row, leaving_var = self._choose_leaving(B_inv, entering, xB)
        if row is None:
            self.status_flag = "unbounded"
            return {"status": "unbounded", "iteration": self.iteration, "entering": entering, "Z": Z}

        # Actual pivot: reemplazar basis[row] por entering
        leaving_index = self.basis[row]
        self.basis[row] = entering

        # registrar iteración
        self.iteration += 1
        snapshot = self.get_tableau_display()
        info = {
            "status": "continue",
            "iteration": self.iteration,
            "entering": entering,
            "entering_name": self.var_names[entering],
            "leaving": leaving_index,
            "leaving_name": self.var_names[leaving_index] if 0 <= leaving_index < len(self.var_names) else str(leaving_index),
            "Z": float(Z),
            "snapshot": snapshot
        }
        self.history.append(info)
        return info


    # ################ Utilidades ################
    def _remove_artificials(self):
        """Elimina columnas artificiales de forma robusta o marca inconsistencia."""
        to_remove = set(self.artificials)
        if not to_remove:
            return

        m = self.A.shape[0]
        old_n = self.A.shape[1]

        # Construir nuevas columnas (no artificiales) y mapeo
        keep_cols = [j for j in range(old_n) if j not in to_remove]
        new_col_list = [ self.A[:, j].copy() for j in keep_cols ]
        new_names = [ self.var_names[j] for j in keep_cols ]
        new_c = [ float(self.c[j]) for j in keep_cols ]

        if len(new_col_list) > 0:
            new_A = np.column_stack(new_col_list)
        else:
            new_A = np.zeros((m, 0))

        # Mapeo old->new
        new_idx_map = { old: new for new, old in enumerate(keep_cols) }

        # Reconstruir basis: intentar mapear cada basic old index a new index
        new_basis = []
        for old_b in self.basis:
            if old_b in to_remove:
                # buscar reemplazo en la fila correspondiente: prefer columna canónica (1 en esa fila y 0 elsewhere)
                row_index = self.basis.index(old_b)
                replacement = None
                for new_j, old_j in enumerate(keep_cols):
                    if abs(new_A[row_index, new_j]) > 1e-9:
                        # candidate: ensure it's not creating multiple nonzeros in other rows? We'll accept and hope pivot can fix
                        replacement = new_j
                        break
                if replacement is None:
                    # No hay columna que pueda reemplazar la básica artificial -> problema potencialmente inconsistente
                    raise RuntimeError("No se encontró columna pivote al eliminar artificiales; modelo inconsistente.")
                new_basis.append(replacement)
            else:
                # simple mapping
                if old_b in new_idx_map:
                    new_basis.append(new_idx_map[old_b])
                else:
                    # shouldn't happen, but guard
                    raise RuntimeError("Error interno al reconstruir base tras eliminar artificiales.")

        # Actualizar estructuras
        self.A = new_A
        self.c = np.array(new_c, dtype=float)
        self.var_names = new_names
        self.basis = new_basis
        self.artificials = []


    # ################ Estado y solución ################
    def is_optimal(self):
        """Devuelve True si el problema está en estado óptimo (fase 2)"""
        if self.status_flag == "optimal":
            return True
        # calcular B_inv y costos reducidos
        B, N, nonbas = self._get_B_and_N()
        if B.size == 0:
            B_inv = np.zeros((self.A.shape[0], self.A.shape[0]))
        else:
            try:
                B_inv = np.linalg.inv(B)
            except np.linalg.LinAlgError:
                B_inv = np.linalg.pinv(B)
        r = self._reduced_costs(B_inv)
        # En fase 1 no se considera "óptimo" para el problema original
        if self.phase == 1:
            # óptimo de fase1 si no hay costos reducidos < -EPS
            return all(r[j] >= -EPS for j in range(len(r)) if j not in self.basis)
        else:
            # fase2: óptimo si no hay costos reducidos > EPS
            return all(r[j] <= EPS for j in range(len(r)) if j not in self.basis)

    def get_tableau_display(self):
        """
        Construye una representación apta para mostrar en la tabla:
        Devuelve lista de filas; cada fila es:
            [BaseName, v1, v2, ..., RHS]
        y una última fila con 'Z' y costos reducidos
        """
        m = self.A.shape[0]
        n = self.A.shape[1]
        B, N, nonbas = self._get_B_and_N()
        try:
            B_inv = np.linalg.inv(B) if B.size>0 else np.zeros((m,m))
        except np.linalg.LinAlgError:
            B_inv = np.linalg.pinv(B)
        xB, Z, _ = self._compute_current_solution()

        # coeficientes completos del tableau para mostrar: B_inv * A da los coeficientes actuales de las básicas en términos de las no básicas
        tableau_rows = []

        # Construir representación de la matriz completa de coeficientes: variables básicas actuales expresadas en términos de todas las variables
        # En vez de eso, produciremos fila: BaseName, coeficientes para todas las variables (A_effective), RHS
        # Calcular vector de solución actual x_full como ceros excepto básicas
        x_full = np.zeros(n)
        for i, bidx in enumerate(self.basis):
            if 0 <= bidx < n:
                x_full[bidx] = xB[i]
        for i in range(m):
            base_idx = self.basis[i]
            row_coeffs = []

            # Representación actual de la fila básica (B_inv * A) fila i
            # calcular row_i = e_i^T * B_inv * A  => (B_inv[i,:].dot(A))
            row_i = B_inv[i,:].dot(self.A) if B_inv.size>0 else np.zeros(n)
            for j in range(n):
                row_coeffs.append(row_i[j])
            rhs_val = xB[i] if i < len(xB) else 0.0
            tableau_rows.append({
                "base_name": self.var_names[base_idx] if 0 <= base_idx < len(self.var_names) else f"b{base_idx}",
                "coeffs": row_coeffs,
                "rhs": rhs_val
            })
        # fila de costos reducidos
        red_costs = self._reduced_costs(B_inv)
        z_row = {
            "base_name": "Z",
            "coeffs": list(red_costs),
            "rhs": Z
        }
        return {
            "var_names": self.var_names.copy(),
            "rows": tableau_rows,
            "z_row": z_row
        }

    def get_solution(self):
        """Devuelve la solución actual (valores de variables y Z)"""
        n = self.A.shape[1]
        x = np.zeros(n)
        xB, Z, _ = self._compute_current_solution()
        for i, bidx in enumerate(self.basis):
            if bidx >= 0 and bidx < n and i < len(xB):
                x[bidx] = xB[i]
        Z_val = Z
        # Si el modo es "Min", revertimos el signo de Z porque el solver convierte Min a Max internamente.
        if self.modo == "Min":
            Z_val = -Z_val
        # Mapear nombres de variables a valores
        sol = { self.var_names[i]: float(x[i]) for i in range(n) }
        sol = { self.var_names[i]: float(x[i]) for i in range(n) }
        sol["Z"] = float(Z_val)
        return sol

    def status(self):
        return self.status_flag
