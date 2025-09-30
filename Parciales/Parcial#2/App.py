# Investigación de Operaciones: Parcial #1: Metodo Gráfico by JDRB
# Codigo Principal

# Menú principal para elegir el método de PL
from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer, Static
from textual.containers import Vertical
import AppTCSS

# Importación de los módulos (pantallas)
from Simplex.Simplex import SimplexApp
from Dual.Dual import DualApp
from AlgoritmoDual.AlgDual import AlgDualApp

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
            yield Button("Método Simplex", id="btnSimplex")
            yield Button("Método Dual", id="btnDual")
            yield Button("Algoritmo Dual Simplex", id="btnAlgDual")

    # Manejo de botones
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btnSimplex":
            self.push_screen(SimplexApp())
        elif event.button.id == "btnDual":
            self.push_screen(DualApp())
        elif event.button.id == "btnAlgDual":
            self.push_screen(AlgDualApp())

# Ejecución de la aplicación
if __name__ == "__main__":
    MenuPrincipal().run()
