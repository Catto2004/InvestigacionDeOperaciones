# Simplex/Simplex.py
# Implementación del algoritmo Simplex para Programación Lineal

from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from . import SimplexTCSS
from . import SolverSimplex
from Parser import Parsear
import MicroModulos
import EjerciciosDemo


class SimplexApp(Screen):
    # ################ Variables de la interfaz ################
    CSS = SimplexTCSS.CSS # cargar el CSS desde SimplexTCSS.py
    BINDINGS = [ 
        ("^b", "back", "Volver al menú"),
        ("^r", "reset", "Resetear"),
        ("^i", "iterate", "Iterar"),
        ("^s", "solve", "Resolver"),
        ("^d", "demo", "Cargar demo")
    ] # atajos de teclado
    TITLE = "Parcial #2 / Algoritmo Simplex" # título de la pantalla

    # ################ Variables del problema ################
    Problema = {"modo": "Max", "funcion_objetivo": "", "restricciones": []} # problema actual
    Iteraciones = [] # iteraciones del proceso
    Solucion = {} # solución final


    # ################ Manejo de la interfaz ################
    # Composición de la interfaz
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with Horizontal(id="PanelPrincipal"):
            with Vertical(id="PanelIzquierdo"):
                yield MicroModulos.WidgetFuncionObjetivo(id="FuncionObjetivo")
                yield MicroModulos.WidgetRestricciones(id="Restricciones")
                yield MicroModulos.WidgetSolucion(id="Solucion")

            with Vertical(id="PanelDerecho"):
                yield MicroModulos.WidgetTablaIteraciones(id="TablaIteraciones")


    # ################ Manejo de Acciones ################
    # Atajo para volver
    async def action_back(self):
        self.app.pop_screen()  # o regresar al menú principal

    # Atajo para resetear todo
    async def action_reset(self):
        # Llamar a reset en widgets
        self.query_one("#Restricciones", MicroModulos.WidgetRestricciones).Reset()
        self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo).Reset()
        self.query_one("#Solucion", MicroModulos.WidgetSolucion).Reset()
        self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones).Reset()
        self.Problema = {"modo": "Max", "funcion_objetivo": "", "restricciones": []}

    # Atajo para iterar un paso   
    def action_iterate(self):
        pass
        
    # función interna para construir matrices c, A, b desde FO y restricciones parseadas
    def action_resolver(self):
        pass

    # Atajo para cargar un ejercicio de demo
    def action_demo(self):
        pass
