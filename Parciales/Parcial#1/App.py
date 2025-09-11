# Investigación de Operaciones: Parcial #1: Metodo Gráfico by JDRB
# Codigo Principal

# ############ Importaciones
from email.header import Header
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Button, Static, Label, Footer, DataTable, Header
from textual.reactive import reactive
import os

import Solver
import Plotter
import tcss

os.system("cls")

# ############ Aplicación
class MetodoGrafico(App):
    # ################## Declaración De Variables ##################
    CSS = tcss.CSS
    TITLE = "Investigación de Operaciones: Parcial #1: Metodo Gráfico by JDRB"
    BINDINGS = [("^q", "quit", "Salir"),  # Cerrar la aplicación
                ("^r", "reset", "Reset")] # Reiniciar la aplicación
    
    restricciones = reactive([])

    def on_mount(self) -> None:
        pass
        #tabla = self.query_one("#TablaRestricciones", DataTable)
        #tabla.add_columns("Restricción")

        #ruta = Plotter.generar_grafica()
        #self.img_widget.path = ruta

    async def AppQuit(self):
        self.exit()

    # ################## Interface ##################
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with Vertical():
            # Panel Principal
            with Horizontal(id="PanelPrincipal"):
                # Panel Izquierdo
                with Vertical(id="PanelIzquierdo"):
                    yield Label("Función objetivo:", id="TituloFunObj")
                    yield Input(placeholder="z = 3x + 4y", id="InputFunObj")
                    yield Label("Restricciones:", id="TituloRestricciones")
                    yield Input(placeholder="Ingrese una restricción...", id="InputRestriccion")
                    yield Static("", id="TablaRestricciones")

                # Panel Derecho
                with Vertical(id="PanelDerecho"):
                    yield Static("Gráfica:", id="TituloGrafica")
                    #yield self.img_widget
                    yield Static("Solución:", id="TituloSolucion")
                    yield Static("", id="Solucion")


    # ################## Manejo de Botones ##################
    def on_button_pressed(self, event: Button.Pressed) -> None:
        boton = event.button

        if boton.id == "BotonSalir":
            self.exit()
            return


# ################## Ejecución ##################
if __name__ == "__main__":
    MetodoGrafico().run()