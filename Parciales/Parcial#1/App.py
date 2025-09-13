# Investigación de Operaciones: Parcial #1: Metodo Gráfico by JDRB
# Codigo Principal

# ############ Importaciones
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Button, Static, Label, Footer, Header
from textual.reactive import reactive
import os

import Plotter
import tcss

os.system("cls")

# ############ Aplicación
class MetodoGrafico(App):
    # ################## Declaración De Variables ##################
    CSS = tcss.CSS
    TITLE = "Investigación de Operaciones: Parcial #1: Metodo Gráfico by JDRB"
    BINDINGS = [("^q", "quit", "Salir"),  # Cerrar la aplicación
                ("^r", "reset", "Reset"), # Reiniciar la aplicación
                ("^s", "solve", "Resolver")] # Resolver el PL
    
    Restricciones = []  # Lista de restricciones
    Modo = reactive("Max")  # MAX o MIN
    FuncionObjetivo = reactive("")  # Función objetivo inicial
    Resultado = {"Estado": "Esperando", "x": 0, "y": 0, "z": 0}

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
                    yield Input(placeholder="3x + 4y", id="InputFunObj")
                # Static para mostrar la solución
                yield Label("Solución:", id="TituloSolucion")
                yield Static(f"  Estado: {self.Resultado['Estado']}", id="Solucion")
                yield Static(f"     x = {self.Resultado['x']:.2f}", id="SolucionX")
                yield Static(f"     y = {self.Resultado['y']:.2f}", id="SolucionY")
                yield Static(f"     z = {self.Resultado['z']:.2f}", id="SolucionZ")

            # Panel Derecho
            with Vertical(id="PanelDerecho"):
                yield Label("Restricciones:", id="TituloRestricciones")
                yield Input(placeholder="Ingrese una restricción...", id="InputRestriccion")
                yield Static("", id="TablaRestricciones")  

    # ################## Manejo de Botones ##################
    def on_button_pressed(self, event: Button.Pressed) -> None:
        boton = event.button

        # Cambia entre MAX y MIN    
        self.Modo = "Min" if self.Modo == "Max" else "Max"
        event.button.label = self.Modo

    # ################## Eventos ##################
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        # Captura cuando el usuario presiona Enter en un input.
        if event.input.id == "InputRestriccion":
            NuevaRestriccion = event.value.strip() # Nueva restricción
            # Validar y agregar la restricción
            try:
                Plotter.ParsearRestriccion(NuevaRestriccion)
            except ValueError as e: # Si no es válida, mostrar error
                self.notify(f"⚠ Restricción inválida: {e} debe ser de la forma 'ax + by <= c'", severity="error")
                return
            if NuevaRestriccion:
                self.Restricciones.append(NuevaRestriccion)
                event.input.value = ""  # Limpiar el input
                self.ActualizarTablaRestricciones()
        elif event.input.id == "InputFunObj":
            self.FuncionObjetivo = event.value.strip()
            try:
                Plotter.ParsearRestriccion(event.value.strip() + "<=0")  # Validar función objetivo
            except ValueError as e:
                self.notify(f"⚠ Función objetivo inválida: {e} debe ser de la forma 'ax + by'", severity="error")
                return

    def ActualizarTablaRestricciones(self):
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
        self.Modo = "Max"
        self.ActualizarTablaRestricciones()
        self.query_one("#MaxMin", Button).label = self.Modo
        self.query_one("#InputFunObj", Input).value = ""
        self.query_one("#Solucion", Static).update("  Estado: Esperando")
        self.query_one("#SolucionX", Static).update("     x = ")
        self.query_one("#SolucionY", Static).update("     y = ")
        self.query_one("#SolucionZ", Static).update("     z = ")
        self.FuncionObjetivo = ""

    async def action_solve(self):
        """Genera la gráfica y resuelve el problema al presionar ^s (Ctrl+S)."""
        if not self.FuncionObjetivo:
            self.notify("⚠ Debe ingresar una función objetivo primero.", severity="error")
            return
        if not self.Restricciones:
            self.notify("⚠ Debe agregar al menos una restricción.", severity="error")
            return
        
        # Dibujar y resolver
        Plotter.DibujarRestricciones(self.FuncionObjetivo, self.Restricciones, modo=self.Modo) 
        resultado = Plotter.resolverPL(self.FuncionObjetivo, self.Restricciones, modo=self.Modo)
        if resultado and resultado.get("estado") == "Optimal":
            self.query_one("#Solucion", Static).update(f"  Estado: {resultado['estado']}")
            self.query_one("#SolucionX", Static).update(f"     x = {resultado['x']:.2f}")
            self.query_one("#SolucionY", Static).update(f"     y = {resultado['y']:.2f}")
            self.query_one("#SolucionZ", Static).update(f"     z = {resultado['z']:.2f}")
        else:
            self.notify(f"⚠ No se encontró solución (estado: {resultado.get('estado')})", severity="warning")

# ################## Ejecución ##################
if __name__ == "__main__":
    MetodoGrafico().run()