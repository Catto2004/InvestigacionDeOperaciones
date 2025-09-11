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
    
    Restricciones = []  # Lista de restricciones
    Modo = reactive("MAX")  # MAX o MIN

    def on_mount(self) -> None:
        pass
        #tabla = self.query_one("#TablaRestricciones", DataTable)
        #tabla.add_columns("Restricción")

        #ruta = Plotter.generar_grafica()
        #self.img_widget.path = ruta

    # ################## Interface ##################
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with Horizontal(id="PanelPrincipal"):
            # Panel Izquierdo
            with Vertical(id="PanelIzquierdo"):
                yield Label("Función objetivo:", id="TituloFunObj")
                # Controles para la función objetivo
                with Horizontal(id="ControlesFunObj"):
                    yield Button("Max", id="MaxMin")
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

        # Cambia entre MAX y MIN    
        self.Modo = "MIN" if self.Modo == "MAX" else "MAX"
        event.button.label = self.Modo

    # ################## Eventos ##################
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        # Captura cuando el usuario presiona Enter en un input.
        if event.input.id == "InputRestriccion":
            NuevaRestriccion = event.value.strip()
            if NuevaRestriccion:
                self.Restricciones.append(NuevaRestriccion)
                event.input.value = ""  # Limpiar el input
                self.actualizar_tabla_restricciones()

    def actualizar_tabla_restricciones(self):
        # Actualiza el Static que muestra las restricciones.
        if self.Restricciones:
            contenido = "\n".join(f"{i+1}. {r}" for i, r in enumerate(self.Restricciones))
        else:
            contenido = "(Sin restricciones)"
        self.query_one("#TablaRestricciones", Static).update(contenido)

    # ################## Acciones ##################
    async def action_reset(self):
        """Reinicia la lista de restricciones."""
        self.Restricciones = []
        self.Modo = "MAX"
        self.actualizar_tabla_restricciones()
        self.query_one("#InputFunObj", Input).value = ""
        self.query_one("#Solucion", Static).update("")

# ################## Ejecución ##################
if __name__ == "__main__":
    MetodoGrafico().run()