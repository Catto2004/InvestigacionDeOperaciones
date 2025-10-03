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

class SimplexApp(Screen):
    CSS = SimplexTCSS.CSS
    BINDINGS = [
        ("^b", "back", "Volver al menú"),
        ("^r", "reset", "Resetear"),
        ("^i", "iterate", "Iterar"),
        ("^s", "solve", "Resolver"),
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
        self.app.pop_screen()  # o regresar al menú principal

    async def action_reset(self):
        # Llamar a reset en widgets
        self.query_one("#Restricciones", MicroModulos.WidgetRestricciones).reset()
        self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo).reset()
        self.query_one("#Solucion", MicroModulos.WidgetSolucion).reset()
        self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones).reset()

    async def action_resolver(self):

        solver = SolverSimplex(c, A, b, modo="Max")
        resultado = solver.resolver()

        # Configurar tabla de iteraciones
        widget = self.query_one("#TablaIteraciones")
        num_cols = solver.tabla.shape[1]
        columnas = [f"C{i}" for i in range(num_cols)]
        widget.ConfigurarColumnas(columnas)

        for i, t in enumerate(resultado["iteraciones"]):
        # puedes aplanar cada fila de la tabla simplex en strings
            for fila in t:
                widget.AgregarIteracion([round(v, 2) for v in fila])



if __name__ == "__main__":
    # Ejecutar la aplicación Simplex
    SimplexApp().run()
    pass