# Parser.py 
# Módulo para parsear y validar restricciones y funciones objetivo
import re

def Parsear(expresion: str) -> dict:
    """
    Parsea una restricción o función objetivo con hasta 10 variables.
    Soporta variables:
      - Con índice: x1, x2, ..., x10
      - Sin índice: x, y, z (equivale a x1, x2, x3)

    Ejemplos válidos:
      "3x + 2y <= 10"
      "-x + 4z = 7"
      "5x2 - x10 >= 20"
    """

    # 1. Buscar operador de restricción
    match = re.search(r"(<=|>=|=)", expresion)
    if not match:
        raise ValueError("Expresión inválida, falta operador (<=, >=, =).")

    operador = match.group(1)
    izquierda, derecha = expresion.split(operador)
    izquierda = izquierda.strip()
    derecha = derecha.strip()

    # 2. Inicializar coeficientes en 0
    coef = [0.0] * 10

    # 3. Regex para términos tipo [+/-]coef * variable
    #    Soporta: 3x1, -2y, +z, x, etc.
    terminos = re.finditer(r"([+-]?\s*\d*)([a-zA-Z]\d*?)", izquierda)

    # Mapeo de letras simples → índices
    mapa_vars = {"x": 0, "y": 1, "z": 2}

    for t in terminos:
        coef_str = t.group(1).replace(" ", "")
        var_str = t.group(2)

        # Determinar índice de la variable
        if var_str in mapa_vars:  # Caso x, y, z
            idx = mapa_vars[var_str]
        elif var_str.startswith("x") and var_str[1:].isdigit():  # Caso x1..x10
            idx = int(var_str[1:]) - 1
        else:
            raise ValueError(f"Variable no reconocida: {var_str}")

        if idx < 0 or idx >= 10:
            raise ValueError(f"Variable fuera de rango: {var_str}")

        # Determinar coeficiente
        if coef_str in ["", "+"]:
            valor = 1.0
        elif coef_str == "-":
            valor = -1.0
        else:
            valor = float(coef_str)

        coef[idx] += valor

    # 4. Constante del lado derecho
    try:
        constante = float(derecha)
    except ValueError:
        raise ValueError(f"Constante inválida: {derecha}")

    return {
        "coef": coef,
        "operador": operador,
        "constante": constante
    }
