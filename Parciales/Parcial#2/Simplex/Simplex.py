# Simplex/Simplex.py
# Implementación del método Simplex para Programación Lineal

from textual.app import ComposeResult, App
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from . import SimplexTCSS
from . import SolverSimplex
import MicroModulos
import EjerciciosDemo

class SimplexApp(App):
    CSS = SimplexTCSS.CSS
    BINDINGS = [
        ("b", "back", "Volver al menú"),
        ("r", "reset", "Resetear"),
        ("q", "quit", "Salir")
    ]

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
    
    async def action_back(self):
        self.exit("back")  # o regresar al menú principal

    async def action_reset(self):
        # Llamar a reset en widgets
        self.query_one("#Restricciones", MicroModulos.WidgetRestricciones).reset()
        self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo).reset()
        self.query_one("#Solucion", MicroModulos.WidgetSolucion).reset()

    async def action_quit(self):
        self.exit()


if __name__ == "__main__":
    # Ejecutar la aplicación Simplex
    SimplexApp().run()
    pass