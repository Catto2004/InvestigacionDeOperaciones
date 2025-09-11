# Investigación de Operaciones: Parcial #1: Metodo Gráfico by JDRB
# Codigo Principal

# ############ Importaciones
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Button, Static, Label
from textual.reactive import reactive
import os

import Solver
import Plotter
import tcss

os.system("cls")

# ############ Aplicación
class App(App):
    CSS = tcss.CSS
    restricciones = reactive([])

    def on_mount(self) -> None:
        self.title = "Parcial #1: Metodo Gráfico"
        self.classes= "-light-mode"
        #tabla = self.query_one("#TablaRestricciones", DataTable)
        #tabla.add_columns("Restricción")

        #ruta = Plotter.generar_grafica()
        #self.img_widget.path = ruta

    # ################## Interface ##################
    def compose(self) -> ComposeResult:
        with Vertical():
            
            # Barra Superior
            with Horizontal(id="BarraSuperior"):
                yield Static("Investigación de Operaciones: Parcial #1: Metodo Gráfico by JDRB", id="Titulo")
                yield Button("Reset", id="BotonReset")
                yield Button("X", id="BotonSalir")

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

if __name__ == "__main__":
    App().run()