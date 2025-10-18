# utils.py
# Utilidades: parseo y validación de función objetivo y restricciones

import re
import numpy as np

# ------------------------------------------------------------
# VALIDACIÓN Y PARSEO
# ------------------------------------------------------------

def validate_input(expression):
    ops = ['<=', '>=', '=', '<', '>']
    return any(op in expression for op in ops)


def parse_constraints(constraints):
    """
    Convierte las restricciones en una lista de tuplas:
    [({'x1':1, 'x2':2}, '<=', 10), ({'x1':1}, '>=', 0)]
    Acepta múltiples restricciones separadas por ';'
    """
    parsed_constraints = []

    for constraint in constraints.split(';'):
        constraint = constraint.strip()
        if not constraint:
            continue

        # Ignorar restricciones de no negatividad explícitas del tipo x1 >= 0
        if re.match(r'^[A-Za-z]\d*\s*[<>]=\s*0$', constraint.replace(' ', '')):
            continue

        if not validate_input(constraint):
            raise ValueError(f"Restricción inválida: {constraint}")

        if '<=' in constraint:
            sign = '<='
        elif '>=' in constraint:
            sign = '>='
        elif '=' in constraint:
            sign = '='
        else:
            raise ValueError(f"Restricción sin operador válido: {constraint}")

        left, right = constraint.split(sign)
        right_val = float(right.strip())
        expr = left.replace('-', '+-')
        terms = expr.split('+')
        coef_dict = {}

        for term in terms:
            term = term.strip()
            if not term:
                continue

            match = re.match(r'(-?\d*\.?\d*)\*?([A-Za-z]\d*)', term)
            if not match:
                raise ValueError(f"Término inválido en restricción: '{term}'")

            coef_str, var = match.groups()
            if coef_str in ['', '+', '-']:
                coef = float(coef_str + '1') if coef_str in ['+', '-'] else 1.0
            else:
                coef = float(coef_str)

            coef_dict[var] = coef

        parsed_constraints.append((coef_dict, sign, right_val))

    return parsed_constraints


def parse_objective_function(objective_function):
    """
    Convierte la función objetivo (string) en un diccionario con coeficientes.
    Ejemplo:
      '3x1 + 2x2 - x3' o '3*x1 + 2*x2'
    -> {'x1': 3.0, 'x2': 2.0, 'x3': -1.0}
    """
    if not objective_function.strip():
        raise ValueError("Función objetivo vacía.")

    expression = objective_function.replace('-', '+-')
    terms = expression.split('+')
    coef_dict = {}

    for term in terms:
        term = term.strip()
        if not term:
            continue

        match = re.match(r'(-?\d*\.?\d*)\*?([A-Za-z]\d*)', term)
        if not match:
            raise ValueError(f"Término inválido en función objetivo: '{term}'")

        coef_str, var = match.groups()
        if coef_str in ['', '+', '-']:
            coef = float(coef_str + '1') if coef_str in ['+', '-'] else 1.0
        else:
            coef = float(coef_str)

        coef_dict[var] = coef

    return coef_dict
