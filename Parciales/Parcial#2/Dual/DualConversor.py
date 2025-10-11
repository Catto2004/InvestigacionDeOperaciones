# DualConversor/DualConversor.py
# Conversión de un problema de programación lineal primal a su forma dual.
import re
import numpy as np


# ################ Parser Interno ################
def Parsear(expresion: str) -> dict:
    """
    Parsea una restricción o función objetivo con hasta 10 variables.
    Retorna: { 'coef': [...], 'operador': <=|>=|=|None, 'constante': float, 'max_var': int }
    """
    match = re.search(r"(<=|>=|=)", expresion)
    if match:
        operador = match.group(1)
        izquierda, derecha = expresion.split(operador)
        izquierda = izquierda.strip()
        derecha = derecha.strip()
    else:
        operador = None
        izquierda = expresion.strip()
        derecha = "0"

    coef = [0.0] * 10
    max_idx = -1

    terminos = re.finditer(r"([+-]?\s*\d*(?:\.\d+)?)\s*([a-zA-Z]\d*)", izquierda)
    mapa_vars = {"x": 0, "y": 1, "z": 2}

    for t in terminos:
        coef_str = t.group(1).replace(" ", "")
        var_str = t.group(2)

        if var_str in mapa_vars:
            idx = mapa_vars[var_str]
        elif var_str.lower().startswith("x") and var_str[1:].isdigit():
            idx = int(var_str[1:]) - 1
        else:
            raise ValueError(f"Variable no reconocida: {var_str}")

        if idx < 0 or idx >= 10:
            raise ValueError(f"Variable fuera de rango (1..10): {var_str}")

        if coef_str in ["", "+"]:
            valor = 1.0
        elif coef_str == "-":
            valor = -1.0
        else:
            valor = float(coef_str)

        coef[idx] += valor
        if idx > max_idx:
            max_idx = idx

    try:
        constante = float(derecha)
    except ValueError:
        raise ValueError(f"Constante inválida: {derecha}")

    return {"coef": coef, "operador": operador, "constante": constante, "max_var": max_idx}


# ################ Formato ################
def fmt_num(x):
    if abs(x - round(x)) < 1e-12:
        return str(int(round(x)))
    else:
        return str(float(x))

def format_linear_combination(coeffs, var_prefix="y"):
    terms = []
    for j, coef in enumerate(coeffs):
        if abs(coef) < 1e-12:
            continue
        abs_coef = abs(coef)
        coef_str = "" if abs(abs_coef - 1) < 1e-12 else f"{fmt_num(abs_coef)}*"
        var_str = f"{var_prefix}{j+1}"
        sign = "-" if coef < 0 else "+"
        terms.append((sign, coef_str + var_str))

    if not terms:
        return "0"
    first_sign, first_term = terms[0]
    s = ("-" if first_sign == "-" else "") + first_term
    for sign, term in terms[1:]:
        s += f" {sign} {term}"
    return s


# ################ Conversor ################
class DualConversor:

    def primal_to_dual(self, c, A, b, tipos, tipo_primal="MAX"):
        """Conversión de PL Primal a Dual"""

        A = np.array(A, dtype=float) if len(A) > 0 else np.zeros((0, len(c)), dtype=float)
        c = np.array(c, dtype=float)
        b = np.array(b, dtype=float)

        m = A.shape[0]   # número de restricciones primal → número de variables dual
        n = A.shape[1]   # número de variables primal → número de restricciones dual

        dual_A = A.T
        tipo_dual = "Min" if tipo_primal.upper() == "MAX" else "Max"

        # Función objetivo dual
        fo_terms = [f"{fmt_num(b[j])}*y{j+1}" for j in range(m) if abs(b[j]) >= 1e-12]
        fo = f"{tipo_dual} W = " + (" + ".join(fo_terms) if fo_terms else "0")

        # Restricciones duales
        op_dual = ">=" if tipo_primal.upper() == "MAX" else "<="
        restricciones = []
        for i in range(n):
            lhs = format_linear_combination(dual_A[i, :], var_prefix="y")
            rhs = fmt_num(c[i]) if i < len(c) else "0"
            restricciones.append(f"{lhs} {op_dual} {rhs}")

        # Condiciones de signo
        condiciones = []
        for j in range(m):
            tipo = tipos[j]
            if tipo_primal.upper() == "MAX":
                if tipo == "<=":
                    condiciones.append(f"y{j+1} >= 0")
                elif tipo == ">=":
                    condiciones.append(f"y{j+1} <= 0")
                elif tipo == "=":
                    condiciones.append(f"y{j+1} libre")
            else:
                if tipo == "<=":
                    condiciones.append(f"y{j+1} <= 0")
                elif tipo == ">=":
                    condiciones.append(f"y{j+1} >= 0")
                elif tipo == "=":
                    condiciones.append(f"y{j+1} libre")

        return tipo_dual, fo, restricciones, condiciones

    # ################ Ejecucion ################
    def Convertir(self, fo_primal: str, restricciones: list[str], tipo_primal="MAX") -> dict:
        """
        Convierte un problema primal a dual.
        fo_primal: str  (ej: "5x1 + 8x2 + 6x3")
        restricciones: lista de strings (ej: ["2x1 + x2 + x3 >= 20", "x1 + x2 + 2x3 >= 25"])
        tipo_primal: "MAX" o "MIN"
        """

        if not fo_primal or not restricciones:
            raise ValueError("Debe especificar función objetivo y al menos una restricción.")

        # Parsear FO
        parsed_fo = Parsear(fo_primal)
        parsed_constraints = []

        for r in restricciones:
            p = Parsear(r)
            # Filtrar no negatividad (xj >= 0 o <= 0 con constante 0)
            nonzero_vars = [abs(c) > 1e-9 for c in p["coef"]]
            if sum(nonzero_vars) == 1 and abs(p["constante"]) < 1e-9:
                continue
            parsed_constraints.append(p)

        if not parsed_constraints:
            raise ValueError("No se encontraron restricciones válidas para el dual.")

        # Determinar número de variables reales
        max_idx = parsed_fo["max_var"]
        for p in parsed_constraints:
            if p["max_var"] > max_idx:
                max_idx = p["max_var"]

        n_vars = max_idx + 1

        c = parsed_fo["coef"][:n_vars]
        A = [p["coef"][:n_vars] for p in parsed_constraints]
        b = [p["constante"] for p in parsed_constraints]
        tipos = [p["operador"] for p in parsed_constraints]

        tipo_dual, fo, restricciones_dual, condiciones = self.primal_to_dual(c, A, b, tipos, tipo_primal)

        return {
            "tipo_dual": tipo_dual,
            "funcion_objetivo": fo,
            "restricciones": restricciones_dual,
            "condiciones": condiciones,
        }