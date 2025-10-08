# Parser.py 
# Módulo para parsear y validar restricciones y funciones objetivo
import re

def Parsear(expresion: str) -> dict:
    """
    Parsea una restricción o función objetivo con hasta 10 variables.
    Acepta variables x1..x10 o letras sin índice (x, y, z).
    """

    # --- 1. Normalización de entrada ---
    if isinstance(expresion, (list, tuple)):
        # Si por error viene como lista (["x1 + x2 <= 10"]), la convertimos
        expresion = " ".join(map(str, expresion))
    if not isinstance(expresion, str):
        raise ValueError(f"Tipo inválido de expresión ({type(expresion).__name__}), se esperaba str.")
    
    expresion = expresion.strip().lower()
    if not expresion:
        raise ValueError("La expresión está vacía.")

    # --- 2. Buscar operador (<=, >=, =) ---
    match = re.search(r"(<=|>=|=)", expresion)
    if not match:
        raise ValueError("Expresión inválida, falta operador (<=, >=, =).")

    operador = match.group(1)
    partes = expresion.split(operador)
    if len(partes) != 2:
        raise ValueError("Expresión mal formada, no se pudo dividir correctamente en lados izquierdo y derecho.")
    
    izquierda, derecha = [p.strip() for p in partes]

    # --- 3. Inicializar coeficientes ---
    coef = [0.0] * 10

    # --- 4. Buscar términos ---
    # Acepta cosas como: 3x, -x2, +4y3, etc.
    terminos = re.finditer(r"([+-]?\s*\d*)([a-zA-Z]\d*?)", izquierda)
    mapa_vars = {"x": 0, "y": 1, "z": 2}

    encontrados = False
    for t in terminos:
        encontrados = True
        coef_str = t.group(1).replace(" ", "")
        var_str = t.group(2)

        # --- índice de variable ---
        if var_str in mapa_vars:
            idx = mapa_vars[var_str]
        elif var_str[0].isalpha() and var_str[1:].isdigit():
            idx = int(var_str[1:]) - 1
        else:
            raise ValueError(f"Variable no reconocida: {var_str}")

        if not (0 <= idx < 10):
            raise ValueError(f"Variable fuera de rango: {var_str}")

        # --- coeficiente ---
        if coef_str in ["", "+"]:
            valor = 1.0
        elif coef_str == "-":
            valor = -1.0
        else:
            try:
                valor = float(coef_str)
            except ValueError:
                raise ValueError(f"Coeficiente inválido en término: '{coef_str}{var_str}'")

        coef[idx] += valor

    if not encontrados:
        raise ValueError("No se detectaron variables válidas en la expresión.")

    # --- 5. Constante derecha ---
    try:
        constante = float(derecha)
    except ValueError:
        raise ValueError(f"Constante inválida: {derecha}")

    return {
        "coef": coef,
        "operador": operador,
        "constante": constante
    }