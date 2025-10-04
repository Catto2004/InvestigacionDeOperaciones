# parser_dual.py
import re
import numpy as np

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

    # términos tipo: (coeficiente opcional) (variable como x, y, z, x1..x10)
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


# ---------- helpers de formateo ----------
def fmt_num(x):
    # Quitar .0 si es entero
    if abs(x - round(x)) < 1e-12:
        return str(int(round(x)))
    else:
        return str(float(x))

def format_linear_combination(coeffs, var_prefix="y"):
    """
    coeffs: iterable de coeficientes (en orden y1,y2,...)
    Devuelve string como "2*y1 + y2 - 3*y3" (omite ceros).
    """
    terms = []
    for j, coef in enumerate(coeffs):
        if abs(coef) < 1e-12:
            continue
        # coeficiente absoluto y representación
        abs_coef = abs(coef)
        coef_str = "" if abs(abs_coef - 1) < 1e-12 else f"{fmt_num(abs_coef)}*"
        var_str = f"{var_prefix}{j+1}"
        term = coef_str + var_str
        sign = "-" if coef < 0 else "+"
        terms.append((sign, term))

    if not terms:
        return "0"
    # montar cadena (primer término sin '+')
    first_sign, first_term = terms[0]
    s = ( "-" if first_sign == "-" else "" ) + first_term
    for sign, term in terms[1:]:
        s += f" {sign} {term}"
    return s


# ---------- conversión primal -> dual ----------
def primal_to_dual(c, A, b, tipos, tipo_primal="MAX"):
    """
    c: lista/array (long n)
    A: lista de filas (m x n)
    b: lista (m)
    tipos: lista de operadores para cada restricción (m) (<=, >=, =)
    tipo_primal: "MAX" o "MIN"
    """
    A = np.array(A, dtype=float) if len(A) > 0 else np.zeros((0, len(c)), dtype=float)
    c = np.array(c, dtype=float)
    b = np.array(b, dtype=float)

    m = A.shape[0]   # número de restricciones primal -> número de variables dual
    n = A.shape[1]   # número de variables primal -> número de restricciones dual

    # transpuesta: shape (n x m)
    dual_A = A.T

    # Determinar tipo de problema dual (opuesto al primal)
    tipo_dual = "Min" if tipo_primal.upper() == "MAX" else "Max"

    # FO dual: Min/Max W = sum b_j * y_j
    fo_terms = []
    for j in range(m):
        if abs(b[j]) < 1e-12:
            continue
        fo_terms.append(f"{fmt_num(b[j])}*y{j+1}")
    fo = f"{tipo_dual} W = " + ( " + ".join(fo_terms) if fo_terms else "0" )

    # restricciones dual: una por cada variable primal (i = 0..n-1)
    # El operador depende del tipo de primal
    op_dual = ">=" if tipo_primal.upper() == "MAX" else "<="
    restricciones = []
    for i in range(n):
        lhs = format_linear_combination(dual_A[i, :], var_prefix="y")
        rhs = fmt_num(c[i]) if i < len(c) else "0"
        restricciones.append(f"{lhs} {op_dual} {rhs}")

    # condiciones de signo de las variables duales
    # CORREGIDO: Invertidas las condiciones
    condiciones = []
    for j in range(m):
        tipo = tipos[j]
        if tipo_primal.upper() == "MAX":
            # Primal MAX
            if tipo == "<=":
                condiciones.append(f"y{j+1} >= 0")
            elif tipo == ">=":
                condiciones.append(f"y{j+1} <= 0")
            elif tipo == "=":
                condiciones.append(f"y{j+1} libre")
        else:
            # Primal MIN
            if tipo == "<=":
                condiciones.append(f"y{j+1} <= 0")
            elif tipo == ">=":
                condiciones.append(f"y{j+1} >= 0")
            elif tipo == "=":
                condiciones.append(f"y{j+1} libre")

    return fo, restricciones, condiciones


# ---------- programa principal ----------
if __name__ == "__main__":
    print("=== Conversor Primal → Dual (soporta <=, >=, =) ===")
    
    # Preguntar tipo de problema primal
    tipo_primal = input("¿El problema primal es MAX o MIN? (por defecto MAX): ").strip().upper()
    if tipo_primal not in ["MAX", "MIN"]:
        tipo_primal = "MAX"
        print(f"Usando tipo por defecto: {tipo_primal}")
    
    fo_primal = input("Ingrese la función objetivo (ej: 3x1 + 5x2): ").strip()
    if not fo_primal:
        raise SystemExit("Función objetivo vacía.")

    parsed_fo = Parsear(fo_primal)
    parsed_constraints = []
    print("Ingrese restricciones (<=, >=, =). Una por línea. ENTER para terminar.")
    while True:
        linea = input("Restricción: ").strip()
        if linea == "":
            break
        p = Parsear(linea)
        if p["operador"] is None:
            raise ValueError("Cada restricción debe contener <=, >= o =.")
        parsed_constraints.append(p)

    # Validar que hay al menos una restricción
    if not parsed_constraints:
        raise ValueError("Debe ingresar al menos una restricción.")

    # determinar número de variables primal (máximo índice en FO o en restricciones)
    max_idx = parsed_fo["max_var"]
    for p in parsed_constraints:
        if p["max_var"] > max_idx:
            max_idx = p["max_var"]
    if max_idx < 0:
        raise ValueError("No se detectaron variables (x1..x10 / x,y,z).")

    n_vars = max_idx + 1

    # recortar/extraer vectores y matriz con la cantidad correcta de variables
    c = parsed_fo["coef"][:n_vars]
    A = [p["coef"][:n_vars] for p in parsed_constraints]
    b = [p["constante"] for p in parsed_constraints]
    tipos = [p["operador"] for p in parsed_constraints]

    fo_dual, restr_duales, condiciones = primal_to_dual(c, A, b, tipos, tipo_primal)

    # imprimir resultado
    print("\n=== Problema Dual generado ===")
    print(fo_dual)
    print("s.a:")
    for r in restr_duales:
        print(f"  {r}")
    print("\nCondiciones variables duales:")
    print("  " + ", ".join(condiciones))