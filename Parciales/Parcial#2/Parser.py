# Parser.py 
# Módulo para parsear y validar restricciones y funciones objetivo
import re

def Parsear(expresion: str) -> dict:
    """
    Parsea una restricción o función objetivo con hasta 10 variables.
    Soporta:
      - Coeficientes con o sin asterisco (3x1, 3*x1)
      - Variables con o sin índice (x, y, z, x1, x2, etc.)
      - Letras mayúsculas o minúsculas
    """
    if not expresion or not expresion.strip():
        raise ValueError("La expresión está vacía.")

    expresion = expresion.strip()

    # 1️⃣ Buscar operador de restricción (<=, >= o =)
    match = re.search(r"(<=|>=|=)", expresion)
    if not match:
        # Si no hay operador, asumimos <= 0 (para funciones objetivo)
        expresion += " <= 0"
        match = re.search(r"(<=|>=|=)", expresion)

    operador = match.group(1)
    izquierda, derecha = expresion.split(operador)
    izquierda = izquierda.strip()
    derecha = derecha.strip()

    # 2️⃣ Inicializar coeficientes
    coef = [0.0] * 10

    # 3️⃣ Buscar términos (ahora también soporta "*", mayúsculas y espacios)
    terminos = re.finditer(r"([+-]?\s*\d*\.?\d*)\s*\*?\s*([a-zA-Z]\d*)", izquierda)

    mapa_vars = {"x": 0, "y": 1, "z": 2}

    variables_encontradas = 0

    for t in terminos:
        coef_str = t.group(1).replace(" ", "")
        var_str = t.group(2).lower()

        # Determinar índice
        if var_str in mapa_vars:
            idx = mapa_vars[var_str]
        elif (var_str.startswith("x") or var_str.startswith("y") or var_str.startswith("z")) and var_str[1:].isdigit():
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
        variables_encontradas += 1

    # 🚨 Verificar que haya al menos una variable
    if variables_encontradas == 0:
        raise ValueError("No se detectaron variables en la entrada.")

    # 4️⃣ Constante del lado derecho
    try:
        constante = float(derecha)
    except ValueError:
        raise ValueError(f"Constante inválida: {derecha}")

    return {
        "coef": coef,
        "operador": operador,
        "constante": constante,
        "max_var": max(i for i, c in enumerate(coef) if c != 0) if variables_encontradas > 0 else 0
    }
