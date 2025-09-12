# Investigación de Operaciones: Parcial #1: Metodo Gráfico by JDRB
# Parseador de restricciones
# Parser.py

import re

# ############ Parseo de Restricciones ############ 
def ParsearRestriccion(restriccion: str) -> dict:
    """
    Parsea una restricción lineal del tipo:
    ax + by <= c
    También soporta casos con solo x o solo y.
    Retorna un diccionario con a, b, operador, c.
    """
    restriccion = restriccion.replace(" ", "")

    # Regex mejorado: detecta a, b y c opcionales, así como operadores <=, >= o =
    patron = r"""
        ^                           # inicio de la cadena
        (?:(?P<a>[+-]?\d*)x)?       # coeficiente de x (opcional)
        (?P<signo_y>[+-])?          # signo antes de y (opcional)
        (?:(?P<b>\d*)y)?            # coeficiente de y (opcional)
        (?P<operador><=|>=|=)       # operador de comparación
        (?P<c>[+-]?\d+(\.\d+)?)     # valor del lado derecho
        $                           # fin de la cadena
    """

    match = re.match(patron, restriccion, re.VERBOSE)
    if not match:
        raise ValueError(f"Restricción inválida: {restriccion}")

    # Coeficientes de x e y
    a = match.group("a")
    b = match.group("b")
    signo_y = match.group("signo_y")

    # Normalizamos valores
    a = float(a) if a not in (None, "", "+", "-") else (1.0 if a in ("", "+") else -1.0) if a is not None else 0.0
    b = float(b) if b not in (None, "", "+", "-") else (1.0 if b in ("", "+") else -1.0) if b is not None else 0.0
    if signo_y == "-":
        b = -b

    operador = match.group("operador")
    c = float(match.group("c"))

    return {"a": a, "b": b, "operador": operador, "c": c}

# Ejemplo de uso:
# restriccion = "2x + y <= 20"
# resultado = ParsearRestriccion(restriccion)
# print(resultado)
# Salida: {'a': 2.0, 'b': 1.0, 'operador': '<=', 'c': 20.0}