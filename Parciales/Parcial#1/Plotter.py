# Investigación de Operaciones: Parcial #1: Metodo Gráfico by JDRB
# Código para graficar las restricciones usando Matplotlib
# Plotter.py
import matplotlib.pyplot as plt
import numpy as np

plt.ion()  # Activar modo interactivo globalmente

# Variables globales para la figura y ejes
FiguraPrincipal, EjePrincipal = plt.subplots()

# ########## Funciones ##########
def DibujarRestricciones(ListaRestricciones: list[str]) -> None:
# Recibe una lista de restricciones en formato de texto, y las dibuja en la ventana de Matplotlib.

    EjePrincipal.cla()  # Limpiar el eje antes de dibujar

    x = np.linspace(0, 20, 200)

    for Restriccion in ListaRestricciones:
        # 🔧 Aquí debes convertir el texto de la restricción a algo que se pueda graficar.
        # Ejemplo temporal: todas las restricciones serán y = 20 - x
        y = 20 - x
        EjePrincipal.plot(x, y, label=Restriccion)

    EjePrincipal.set_xlim(0, 20)
    EjePrincipal.set_ylim(0, 20)
    EjePrincipal.legend()
    FiguraPrincipal.canvas.draw()  # Refrescar la ventana

def MostrarGrafica() -> None:
    """
    Muestra la ventana de Matplotlib (si no se está mostrando ya).
    """
    plt.show(block=False)
