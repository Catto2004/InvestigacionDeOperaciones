# DualSolver.py
import re
import numpy as np
from scipy.optimize import linprog

def parsear(expresion: str, n: int):
    """
    Parsea una restricción o función objetivo con hasta n variables.
    Retorna coeficientes, operador y constante.
    """
    match = re.search(r"(<=|>=|=)", expresion)
    if not match:
        raise ValueError("Expresión inválida, falta operador (<=, >=, =).")

    operador = match.group(1)
    izquierda, derecha = expresion.split(operador)
    izquierda, derecha = izquierda.strip(), derecha.strip()

    coef = [0.0] * n
    terminos = re.finditer(r"([+-]?\s*\d*)(x\d+)", izquierda)

    for t in terminos:
        coef_str = t.group(1).replace(" ", "")
        var_str = t.group(2)
        idx = int(var_str[1:]) - 1
        if coef_str in ["", "+"]:
            valor = 1.0
        elif coef_str == "-":
            valor = -1.0
        else:
            valor = float(coef_str)
        coef[idx] += valor

    constante = float(derecha)
    return coef, operador, constante

def main():
    print("=== Solver de Programación Lineal (Método Primal/Dual) ===")
    modo = input("\n¿Desea maximizar o minimizar? (max/min): ").strip().lower()

    # Función objetivo
    fo = input("\nIngrese la función objetivo (ej: 3x1 + 5x2): ")
    # Detectar número de variables
    variables = re.findall(r"x(\d+)", fo)
    n = max(int(v) for v in variables)

    c, _, _ = parsear(fo + " = 0", n)  # truco: lo tratamos como restricción
    c = np.array(c)

    if modo == "max":
        c = -c  # linprog minimiza siempre

    m = int(input("\nIngrese el número de restricciones: "))
    A = []
    b = []

    for i in range(m):
        restr = input(f"Restricción {i+1}: ")
        coef, op, cons = parsear(restr, n)

        if op == "<=":
            A.append(coef)
            b.append(cons)
        elif op == ">=":
            A.append([-a for a in coef])
            b.append(-cons)
        elif op == "=":
            # Se parte en dos
            A.append(coef)
            b.append(cons)
            A.append([-a for a in coef])
            b.append(-cons)

    res = linprog(c, A_ub=A, b_ub=b, bounds=[(0, None)]*n, method="highs")

    if res.success:
        print("\n=== RESULTADO ÓPTIMO ===")
        z = res.fun if modo == "min" else -res.fun
        print(f"Valor óptimo Z = {z:.2f}")
        for i, val in enumerate(res.x, start=1):
            print(f"x{i} = {val:.2f}")
    else:
        print("No se encontró solución factible.")

if __name__ == "__main__":
    main()
