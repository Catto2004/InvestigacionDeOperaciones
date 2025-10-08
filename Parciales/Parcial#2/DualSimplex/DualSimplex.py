# DualSimplex/DualSimplex.py
# Implementación del Algoritmo Dual para Programación Lineal
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

# Conexión al directorio padre (Parcial#2) para pruebas individuales
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from . import DualSimplexTCSS
from Simplex.Simplex import SolverSimplex
from Dual.Dual import DualConversor

import MicroModulos
import EjerciciosDemo

class DualSimplexApp(Screen):
    CSS = DualSimplexTCSS.CSS
    BINDINGS = [
        ("b", "back", "Volver al menú"),
        ("r", "reset", "Resetear"),
        ("s", "solve", "Iterar"),
        ("q", "quit", "Salir")
    ]
    TITLE = "Parcial #2 / Algoritmo Dual Simplex."

    # ################ Variables del problema ################
    Problema = {"modo": "Min", "funcion_objetivo": "", "restricciones": []}   # Problema actual
    Iteraciones = [] # Iteraciones del proceso
    Solucion = {}   # Solución final