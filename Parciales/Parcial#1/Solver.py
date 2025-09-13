import pulp
from Parser import ParsearRestriccion

def resolverPL(funcionObjetivo: str, listaRestricciones: list, modo: str = "MAX") -> dict:
    """
    Resuelve un problema de PL de 2 variables.
    - funcionObjetivo: string tipo "3x+4y"
    - listaRestricciones: ["2x+y<=20", "x+2y<=20"]
    - modo: "MAX" o "MIN"
    """

    # Variables de decisión
    x = pulp.LpVariable("x", lowBound=0)
    y = pulp.LpVariable("y", lowBound=0)

    # Definir problema
    prob = pulp.LpProblem("PL", pulp.LpMaximize if modo == "Max" else pulp.LpMinimize)

    # Parsear función objetivo
    f = ParsearRestriccion(funcionObjetivo + "=0")  # reutilizamos el parser
    prob += f["a"] * x + f["b"] * y, "FunciónObjetivo"

    # Parsear y añadir restricciones
    for restr in listaRestricciones:
        r = ParsearRestriccion(restr)
        if r["operador"] == "<=":
            prob += r["a"] * x + r["b"] * y <= r["c"]
        elif r["operador"] == ">=":
            prob += r["a"] * x + r["b"] * y >= r["c"]
        else: # operador == "="
            prob += r["a"] * x + r["b"] * y == r["c"]

    # Resolver
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    return {
        "estado": pulp.LpStatus[prob.status],
        "x": x.value(),
        "y": y.value(),
        "z": pulp.value(prob.objective)
    }
