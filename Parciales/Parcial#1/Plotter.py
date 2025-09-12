# Investigación de Operaciones: Parcial #1: Metodo Gráfico by JDRB
# Código para graficar las restricciones usando Matplotlib
# Plotter.py

import matplotlib.pyplot as plt
import numpy as np

import Parser

fig, ax = plt.subplots()

# ############ Dibujar Restricciones ############
def DibujarRestricciones(listaRestricciones):
    x = np.linspace(0, 20, 400)
    plt.figure()

    # Guardamos info para sombrear la región factible
    restriccionesProcesadas = []

    for restriccion in listaRestricciones:
        datos = Parser.ParsearRestriccion(restriccion)
        a, b, c, operador = datos["a"], datos["b"], datos["c"], datos["operador"]

        if b != 0:
            y = (c - a * x) / b
            plt.plot(x, y, label=restriccion)
            restriccionesProcesadas.append((a, b, c, operador, y))
        else:
            # Caso especial: no hay término en y => línea vertical
            x_linea = np.full_like(x, c / a)
            plt.plot(x_linea, x, label=restriccion)
            # Para sombrear: usamos máscara booleana
            restriccionesProcesadas.append((a, b, c, operador, None))

    # Sombreado de la región factible
    if restriccionesProcesadas:
        y_max = np.full_like(x, np.inf)
        y_min = np.full_like(x, -np.inf)

        for a, b, c, operador, y in restriccionesProcesadas:
            if b != 0:
                if operador == "<=":
                    y_max = np.minimum(y_max, y)
                elif operador == ">=":
                    y_min = np.maximum(y_min, y)
            else:
                # Restricciones verticales: filtramos dominio de x
                x_valid = x <= c/a if operador == "<=" else x >= c/a
                y_max = np.where(x_valid, y_max, np.nan)
                y_min = np.where(x_valid, y_min, np.nan)

        # Sombreado entre y_min y y_max
        plt.fill_between(x, y_min, y_max, where=(y_max > y_min), color="gray", alpha=0.3)

    plt.xlim(0, 20)
    plt.ylim(-20, 20)
    plt.grid()
    plt.legend()
    plt.show()

# Ejemplo de uso:
# DibujarRestricciones(["2x + y <= 20", "x + 3y <= 30", "x >= 0", "y >= 0"])
# input("Presiona ENTER para cerrar...")  # Mantener la ventana abierta
# plt.ioff()
# plt.show()