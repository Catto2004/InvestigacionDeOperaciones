# Investigación de Operaciones: Parcial #1: Metodo Gráfico by JDRB
# Código para graficar las restricciones usando Matplotlib
# Plotter.py

import matplotlib.pyplot as plt
import numpy as np

from Parser import ParsearRestriccion
from Solver import resolverPL

fig, ax = plt.subplots()

# ############ Dibujar Restricciones ############
def DibujarRestricciones(funcionObjetivo: str, listaRestricciones: list, modo: str = "MAX"):
    """
    Dibuja todas las restricciones, el área factible y el punto óptimo si existe.
    """
    x_vals = np.linspace(0, 20, 400)
    y_vals = np.linspace(0, 20, 400)
    X, Y = np.meshgrid(x_vals, y_vals)

    fig, ax = plt.subplots()
    mascara = np.ones_like(X, dtype=bool)

    # Dibujar restricciones
    for restriccion in listaRestricciones:
        try:
            datos = ParsearRestriccion(restriccion)
        except ValueError as e:
            print(f"⚠ No se pudo interpretar '{restriccion}': {e}")
            continue

        a, b, c, operador = datos["a"], datos["b"], datos["c"], datos["operador"]

        if b != 0:
            y_linea = (c - a * x_vals) / b
            ax.plot(x_vals, y_linea, label=restriccion)
            if operador == "<=":
                mascara &= (a * X + b * Y <= c)
            elif operador == ">=":
                mascara &= (a * X + b * Y >= c)
            else:
                mascara &= np.isclose(a * X + b * Y, c, atol=1e-3)
        else:
            # Línea vertical (no hay y)
            x_linea = np.full_like(x_vals, c / a)
            ax.plot(x_linea, x_vals, label=restriccion)
            if operador == "<=":
                mascara &= (a * X <= c)
            elif operador == ">=":
                mascara &= (a * X >= c)
            else:
                mascara &= np.isclose(a * X, c, atol=1e-3)

    # Sombrear región factible
    ax.contourf(X, Y, mascara, levels=[0.5, 1], colors=["#c2f0c2"], alpha=0.4)

    # Resolver PL y marcar punto óptimo
    resultado = resolverPL(funcionObjetivo, listaRestricciones, modo)
    if resultado["estado"] == "Optimal" and resultado["x"] is not None and resultado["y"] is not None:
        ax.scatter(resultado["x"], resultado["y"], color="red", s=80, zorder=5, label="Óptimo")
        ax.annotate(
            f"z = {resultado['z']:.2f}",
            (resultado["x"], resultado["y"]),
            textcoords="offset points",
            xytext=(5, 5),
            color="red"
        )
    else:
        print(f"⚠ No se encontró solución óptima. Estado: {resultado['estado']}")

    ax.set_xlim(0, 20)
    ax.set_ylim(0, 20)
    ax.grid()
    ax.legend()
    plt.show()

# Ejemplo de uso:
# DibujarRestricciones(["2x + y <= 20", "x + 3y <= 30", "x >= 0", "y >= 0"])
# input("Presiona ENTER para cerrar...")  # Mantener la ventana abierta
# plt.ioff()
# plt.show()