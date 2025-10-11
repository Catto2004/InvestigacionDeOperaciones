# DualSimplex/SolverDualSimplex.py
# Implementación del Algoritmo DUAL SIMPLEX para Programación Lineal
# El Dual Simplex mantiene optimalidad dual mientras busca factibilidad primal

import numpy as np
import sys
import os

# Importar el parser desde el directorio padre
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Parser import Parsear

EPS = 1e-9

class SolverDualSimplex:
    """
    Solver del Método DUAL SIMPLEX paso a paso.
    
    Diferencias con Simplex Primal:
    - Mantiene OPTIMALIDAD DUAL (costos reducidos óptimos)
    - Busca FACTIBILIDAD PRIMAL (variables básicas >= 0)
    - Variable SALIENTE: la más negativa (infactible)
    - Variable ENTRANTE: por razón dual mínima
    
    Uso:
        solver = DualSimplexSolver()
        solver.initialize(modo, funcion_objetivo_str, restricciones_list)
        while not solver.is_optimal():
            info = solver.iterate_one()
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.modo = "Max"
        self.var_names = []
        self.A = None
        self.b = None
        self.c = None
        self.basis = []
        self.iteration = 0
        self.status_flag = "initialized"
        self.history = []
        self.phase = 2  # Dual Simplex trabaja directamente en fase II


    # ################ Inicialización ################
    def initialize(self, modo: str, funcion_objetivo: str, restricciones: list[str]):
        """
        Inicializa el problema para Dual Simplex.
        IMPORTANTE: El problema debe tener optimalidad dual inicial
        (todos los costos reducidos deben ser óptimos para el modo dado)
        """
        self.reset()
        self.modo = modo if modo in ("Max", "Min") else "Max"

        # Parsear función objetivo
        if not any(op in funcion_objetivo for op in ("<=", ">=", "=")):
            parsed_fo = Parsear(funcion_objetivo + " <= 0")
        else:
            parsed_fo = Parsear(funcion_objetivo)
        
        # Parsear restricciones
        parsed_constraints = [Parsear(r) for r in restricciones]

        # Determinar número de variables originales
        max_idx = parsed_fo.get("max_var", -1)
        for p in parsed_constraints:
            if p.get("max_var", -1) > max_idx:
                max_idx = p["max_var"]
        
        if max_idx < 0:
            raise ValueError("No se detectaron variables en la entrada.")

        n_orig = max_idx + 1
        c_orig = parsed_fo["coef"][:n_orig]

        # Construcción de la forma estándar
        A_rows = []
        b = []
        var_names = [f"x{i+1}" for i in range(n_orig)]
        c = list(c_orig)
        basis = []
        s_count = 0

        # Procesar restricciones y añadir variables de holgura
        for ridx, p in enumerate(parsed_constraints):
            row = p["coef"][:n_orig]
            oper = p["operador"]
            rhs = p["constante"]

            if oper == "<=":
                # Añadir slack positivo
                s_count += 1
                row.extend([1.0])
                var_names.append(f"s{s_count}")
                c.append(0.0)
                basis.append(len(c) - 1)
            
            elif oper == ">=":
                # Añadir surplus negativo (para >= multiplicamos por -1)
                # Convertir: a1*x1 + a2*x2 >= b  →  -a1*x1 - a2*x2 + s = -b
                row = [-coef for coef in row]
                rhs = -rhs
                s_count += 1
                row.extend([1.0])
                var_names.append(f"s{s_count}")
                c.append(0.0)
                basis.append(len(c) - 1)
            
            elif oper == "=" or oper is None:
                # Para igualdad, añadir artificial (en Dual Simplex necesitamos base inicial)
                s_count += 1
                row.extend([1.0])
                var_names.append(f"s{s_count}")
                c.append(0.0)
                basis.append(len(c) - 1)
            
            else:
                raise ValueError(f"Operador no soportado: {oper}")

            A_rows.append(row)
            b.append(rhs)

        # Normalizar longitud de filas
        n_total = len(c)
        for i in range(len(A_rows)):
            if len(A_rows[i]) < n_total:
                A_rows[i].extend([0.0] * (n_total - len(A_rows[i])))

        # Guardar estructuras
        self.var_names = var_names
        self.A = np.array(A_rows, dtype=float)
        self.b = np.array(b, dtype=float)
        
        # Convertir a Max interno si es Min
        if self.modo == "Min":
            self.c = np.array([-float(v) for v in c], dtype=float)
        else:
            self.c = np.array(c, dtype=float)

        self.basis = basis.copy()
        self.iteration = 0
        self.status_flag = "ready"

        # Verificar optimalidad dual inicial
        if not self.check_dual_feasibility():
            print("⚠️ Advertencia: el problema no tiene optimalidad dual inicial (r_j > 0 para alguna variable no básica).")



    # ################ Cálculos Internos ################
    def _get_B_and_inv(self):
        """Obtiene matriz básica B y su inversa"""
        m = self.A.shape[0]
        Bcols = [self.A[:, j] for j in self.basis]
        B = np.column_stack(Bcols) if len(Bcols) > 0 else np.zeros((m, 0))
        
        try:
            B_inv = np.linalg.inv(B) if B.size > 0 else np.zeros((m, m))
        except np.linalg.LinAlgError:
            B_inv = np.linalg.pinv(B)
        
        return B, B_inv


    def _compute_current_solution(self):
        """Calcula solución básica actual"""
        B, B_inv = self._get_B_and_inv()
        
        if B_inv.size == 0:
            xB = np.zeros(0)
        else:
            xB = B_inv.dot(self.b)
        
        # Calcular valor objetivo
        cB = np.array([self.c[j] for j in self.basis]) if len(self.basis) > 0 else np.zeros(0)
        Z = float(cB.dot(xB)) if xB.size > 0 else 0.0
        
        return xB, Z, B_inv


    def _reduced_costs(self, B_inv):
        """Calcula costos reducidos"""
        m = self.A.shape[0]
        n = self.A.shape[1]
        
        cB = np.array([self.c[j] for j in self.basis]) if len(self.basis) > 0 else np.zeros(0)
        yT = cB.dot(B_inv) if B_inv is not None and cB.size > 0 else np.zeros((m,))
        
        r = np.zeros(n)
        for j in range(n):
            if j in self.basis:
                r[j] = 0.0
            else:
                a_j = self.A[:, j]
                r[j] = self.c[j] - yT.dot(a_j)
        
        return r


    # ################ Método Dual Simplex: Selección de Variables ################
    def _choose_leaving_dual(self, xB):
        """
        REGLA DUAL: Variable SALIENTE es la básica MÁS NEGATIVA (infactible)
        Retorna: (índice en basis, valor de la variable)
        """
        min_val = 0
        leaving_row = None
        
        for i, val in enumerate(xB):
            if val < min_val - EPS:  # Buscar la más negativa
                min_val = val
                leaving_row = i
        
        if leaving_row is None:
            return None, None
        
        return leaving_row, self.basis[leaving_row]


    def _choose_entering_dual(self, B_inv, leaving_row, r):
        """
        REGLA DUAL: Variable ENTRANTE por razón dual mínima
        
        Para fila saliente k, calcular:
        - y_k = fila k de B_inv (multiplicadores simplex)
        - Para cada no básica j: calcular y_kj = y_k · A[:,j]
        
        Si maximizando:
            - Considerar j donde y_kj < 0
            - Elegir j que minimiza |r_j / y_kj|
        
        Si minimizando:
            - Considerar j donde y_kj > 0  
            - Elegir j que minimiza |r_j / y_kj|
        """
        if leaving_row is None:
            return None
        
        # Obtener fila k de B_inv (multiplicadores para restricción k)
        y_k = B_inv[leaving_row, :]
        
        # Calcular productos y_kj para cada columna no básica
        n = self.A.shape[1]
        nonbas = [j for j in range(n) if j not in self.basis]
        
        ratios = []
        for j in nonbas:
            a_j = self.A[:, j]
            y_kj = y_k.dot(a_j)
            
            # Regla según optimización (internamente siempre Max por conversión)
            if y_kj < -EPS:  # Para Max, necesitamos y_kj < 0
                ratio = abs(r[j] / y_kj)
                ratios.append((ratio, j, y_kj))
        
        if not ratios:
            return None
        
        # Elegir la razón mínima (regla de Bland para desempate)
        ratios.sort(key=lambda x: (x[0], x[1]))
        return ratios[0][1]  # índice de variable entrante


    # ################ Iteración Dual Simplex ################
    def iterate_one(self):
        """
        Ejecuta UNA iteración del Método Dual Simplex:
        1. Verificar optimalidad dual (todos r_j correctos)
        2. Verificar factibilidad primal (todos xB >= 0)
        3. Si infactible: elegir variable saliente (más negativa)
        4. Elegir variable entrante (razón dual mínima)
        5. Pivotear
        """
        if self.status_flag in ("optimal", "unbounded", "infeasible"):
            return {"status": self.status_flag}

        # Calcular solución actual
        xB, Z, B_inv = self._compute_current_solution()
        r = self._reduced_costs(B_inv)

        # VERIFICAR OPTIMALIDAD DUAL (costos reducidos correctos)
        # Para Max: todos r_j <= 0 para no básicas
        # (Internamente siempre trabajamos como Max)
        dual_optimal = all(r[j] <= EPS for j in range(len(r)) if j not in self.basis)
        
        if not dual_optimal:
            self.status_flag = "dual_infeasible"
            return {
                "status": "dual_infeasible",
                "message": "Problema no tiene optimalidad dual inicial",
                "iteration": self.iteration
            }

        # VERIFICAR FACTIBILIDAD PRIMAL (todas básicas >= 0)
        primal_feasible = all(xB[i] >= -EPS for i in range(len(xB)))
        
        if primal_feasible:
            # ¡ÓPTIMO! Tenemos optimalidad dual Y factibilidad primal
            self.status_flag = "optimal"
            return {
                "status": "optimal",
                "iteration": self.iteration,
                "Z": Z,
                "snapshot": self.get_tableau_display()
            }

        # PASO DUAL: Elegir variable SALIENTE (la más negativa)
        leaving_row, leaving_var = self._choose_leaving_dual(xB)
        
        if leaving_row is None:
            # No debería pasar si detectamos infactibilidad correctamente
            self.status_flag = "error"
            return {"status": "error", "message": "No se encontró variable saliente"}

        # PASO DUAL: Elegir variable ENTRANTE (razón dual mínima)
        entering = self._choose_entering_dual(B_inv, leaving_row, r)
        
        if entering is None:
            # No hay variable entrante válida → problema infactible
            self.status_flag = "infeasible"
            return {
                "status": "infeasible",
                "iteration": self.iteration,
                "message": "No existe solución factible (Dual Simplex)",
                "leaving": self.basis[leaving_row]
            }

        # PIVOTEAR: Reemplazar básica
        leaving_index = self.basis[leaving_row]
        self.basis[leaving_row] = entering

        # Actualizar iteración
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
            "snapshot": snapshot,
            "primal_infeasibility": float(min(xB)),  # Qué tan infactible estamos
        }
        
        self.history.append(info)
        return info


    # ################ Estado y Solución ################
    def is_optimal(self):
        """Verifica si estamos en óptimo (dual óptimo Y primal factible)"""
        if self.status_flag == "optimal":
            return True
        
        xB, Z, B_inv = self._compute_current_solution()
        r = self._reduced_costs(B_inv)
        
        # Verificar optimalidad dual
        dual_optimal = all(r[j] <= EPS for j in range(len(r)) if j not in self.basis)
        
        # Verificar factibilidad primal
        primal_feasible = all(xB[i] >= -EPS for i in range(len(xB)))
        
        return dual_optimal and primal_feasible


    def get_tableau_display(self):
        """Construye representación del tableau para visualización"""
        m = self.A.shape[0]
        n = self.A.shape[1]
        
        xB, Z, B_inv = self._compute_current_solution()
        
        tableau_rows = []
        for i in range(m):
            base_idx = self.basis[i]
            row_i = B_inv[i, :].dot(self.A) if B_inv.size > 0 else np.zeros(n)
            rhs_val = xB[i] if i < len(xB) else 0.0
            
            tableau_rows.append({
                "base_name": self.var_names[base_idx] if 0 <= base_idx < len(self.var_names) else f"b{base_idx}",
                "coeffs": list(row_i),
                "rhs": rhs_val,
                "is_feasible": rhs_val >= -EPS  # Indicador de factibilidad
            })
        
        # Fila de costos reducidos
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
        """Retorna solución actual"""
        n = self.A.shape[1]
        x = np.zeros(n)
        xB, Z, _ = self._compute_current_solution()
        
        for i, bidx in enumerate(self.basis):
            if 0 <= bidx < n and i < len(xB):
                x[bidx] = xB[i]
        
        Z_val = Z
        if self.modo == "Min":
            Z_val = -Z_val
        
        sol = {self.var_names[i]: float(x[i]) for i in range(n)}
        sol["Z"] = float(Z_val)
        
        return sol


    def status(self):
        return self.status_flag


    # ################ Métodos de Diagnóstico ################
    def check_dual_feasibility(self):
        """Verifica si el problema tiene optimalidad dual"""
        if self.A is None:
            return False
        
        _, _, B_inv = self._compute_current_solution()
        r = self._reduced_costs(B_inv)
        
        # Para Max: todos r_j <= 0
        return all(r[j] <= EPS for j in range(len(r)) if j not in self.basis)


    def check_primal_feasibility(self):
        """Verifica si la solución es primalmente factible"""
        if self.A is None:
            return False
        
        xB, _, _ = self._compute_current_solution()
        return all(xB[i] >= -EPS for i in range(len(xB)))


    def get_infeasibility_measure(self):
        """Retorna medida de infactibilidad primal (suma de valores negativos)"""
        xB, _, _ = self._compute_current_solution()
        return sum(abs(min(0, x)) for x in xB)