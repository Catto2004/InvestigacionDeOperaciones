# Investigación de Operaciones: Parcial #1: Metodo Gráfico by JDRB
# Codigo Principal

# Menú principal para elegir el método de PL
from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer, Static
from textual.containers import Vertical
import AppTCSS

# Importación de los módulos (pantallas)
from Simplex.Simplex import SimplexApp, SimplexTCSS, SolverSimplex
from Dual.Dual import DualApp, DualTCSS, SolverDual
from AlgoritmoDual.AlgDual import AlgDualApp, AlgDualTCSS, SolverAlgDual

# Clase principal del menú
class MenuPrincipal(App):
    CSS = AppTCSS.CSS
    TITLE = "Investigación de Operaciones - Métodos de PL"
    BINDINGS = [("q", "quit", "Salir")]

    # Composición de la interfaz
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Vertical(id="menu"):
            yield Static("Seleccione el método a utilizar:", id="tituloMenu")
            yield Button("Método Simplex", id="botonSimplex")
            yield Button("Método Dual", id="botonDual")
            yield Button("Algoritmo Dual Simplex", id="botonAlgDual")

    # Manejo de botones
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "botonSimplex":
            self.push_screen(SimplexApp())
        elif event.button.id == "botonDual":
            self.push_screen(DualApp())
        elif event.button.id == "botonAlgDual":
            self.push_screen(AlgDualApp())

# Ejecución de la aplicación
if __name__ == "__main__":
    MenuPrincipal().run()
