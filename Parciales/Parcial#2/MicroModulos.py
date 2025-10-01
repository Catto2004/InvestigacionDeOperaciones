# MicroModulos.py
# Módulo que agrupa las importaciones necesarias para los modulos de la aplicación

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Input, Button, Static, Label, DataTable
from textual.reactive import reactive

import Parser

# ############### Widget "Restricciones"
class WidgetRestricciones(Container):
    restricciones = reactive([])

    def compose(self):
        with Vertical(id="WidgetRestricciones"):
            yield Label("Restricciones:", id="TituloRestricciones")
            yield Input(placeholder="Ingrese una restricción...", id="InputRestriccion")
            yield Static("(Sin restricciones)", id="TablaRestricciones")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "InputRestriccion":
            nueva = event.value.strip()
            try:
                Parser.Parsear(nueva)  # validar
            except ValueError as e:
                self.notify(f"⚠ Restricción inválida: {e}", severity="error")
                return
            self.restricciones.append(nueva)
            event.input.value = ""
            self.ActualizarTabla()

    def ActualizarTabla(self):
        if self.restricciones:
            contenido = "\n".join(f"{i+1}. {r}" for i, r in enumerate(self.restricciones))
        else:
            contenido = "(Sin restricciones)"
        self.query_one("#TablaRestricciones", Static).update(contenido)

    def GetRestricciones(self):
        return self.restricciones



# ############### Widget "Función Objetivo" 
class WidgetFuncionObjetivo(Container):
    modo = reactive("Max")
    funcion_objetivo = reactive("")

    # Composición del widget
    def compose(self):
        with Container(id="WidgetFuncionObjetivo"):
            yield Label("Función objetivo:", id="TituloFunObj")
            with Horizontal(id="ControlesFunObj"):
                yield Button(self.modo, id="MaxMin")
                yield Input(placeholder="3x + 4y", id="InputFunObj")

    # Manejo de botones
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "MaxMin":
            self.modo = "Min" if self.modo == "Max" else "Max"
            event.button.label = self.modo

    # Evento al enviar el input
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "InputFunObj":
            self.funcion_objetivo = event.value.strip()
            try:
                Parser.Parsear(self.funcion_objetivo + "<=0")
            except ValueError as e:
                self.notify(f"⚠ Función objetivo inválida: {e}", severity="error")

    # Obtener función objetivo y modo
    def GetFuncionObjetivo(self):
        return (self.funcion_objetivo, self.modo)



# ############### Widget "Solución"
class WidgetSolucion(Container):
    Resultado = reactive({"Estado": "No resuelto", "Z": 0.0})

    def compose(self):
        with Vertical(id="WidgetSolucion"):
            yield Label("Solución:", id="TituloSolucion")
            yield Label(f"Estado: {self.Resultado['Estado']}", id="SolucionEstado")
            TablaSolucion = DataTable(id="TablaSolucion")
            TablaSolucion.add_columns("Variable", "Valor")
            yield TablaSolucion

    def ActualizarSolucion(self, NuevoResultado: dict):
        """Actualiza la vista de la solución en la tabla."""
        self.Resultado = NuevoResultado

        # Actualizar estado
        self.query_one("#SolucionEstado", Label).update(f"Estado: {self.Resultado.get('Estado', 'Desconocido')}")

        # Limpiar tabla antes de llenarla de nuevo
        TablaSolucion = self.query_one("#TablaSolucion", DataTable)
        TablaSolucion.clear()

        # Ordenar variables (X1..XN primero y Z al final si existe)
        Variables = sorted(
            [k for k in self.Resultado.keys() if k not in ["Estado", "Z"]],
            key=lambda v: int(v[1:]) if v.startswith("X") and v[1:].isdigit() else v
        )
        if "Z" in self.Resultado:
            Variables.append("Z")

        # Agregar filas
        for Var in Variables:
            TablaSolucion.add_row(Var, f"{self.Resultado[Var]:.2f}")

    def ResetSolucion(self):
        """Reinicia la solución a estado inicial."""
        self.ActualizarSolucion({"Estado": "No resuelto", "Z": 0.0})

    def GetSolucion(self):
        """Devuelve el estado actual como dict (por si se necesita)."""
        return self.Resultado



# ############### Widget "Tabla de Iteraciones" 
class WidgetTablaIteraciones(App):
    Contenido = reactive([])  # Lista de listas para las filas de la tabla
    Columnas = reactive([])   # Lista de nombres de columnas

    def compose(self):
        with Vertical(id="WidgetTablaIteraciones"):
            yield Label("Iteraciones:", id="TituloIteraciones")
            TablaIteraciones = DataTable(id="TablaIteraciones")
            yield TablaIteraciones

    def ConfigurarColumnas(self, Columnas: list):
        """Configura las columnas de la tabla de iteraciones."""
        self.Columnas = Columnas
        TablaIteraciones = self.query_one("#TablaIteraciones", DataTable)
        TablaIteraciones.clear(columns=True)
        TablaIteraciones.add_columns(*self.Columnas)

    def AgregarIteracion(self, Fila: list):
        """Agrega una fila de iteración (debe coincidir con el número de columnas)."""
        if len(Fila) != len(self.Columnas):
            raise ValueError("La fila no coincide con el número de columnas.")
        self.Contenido.append(Fila)
        TablaIteraciones = self.query_one("#TablaIteraciones", DataTable)
        TablaIteraciones.add_row(*[str(v) for v in Fila])

    def ResetIteraciones(self):
        """Reinicia la tabla de iteraciones."""
        self.Contenido = []
        TablaIteraciones = self.query_one("#TablaIteraciones", DataTable)
        TablaIteraciones.clear()

    def GetIteraciones(self):
        """Devuelve todas las iteraciones almacenadas."""
        return self.Contenido

# Pruebas
if __name__ == "__main__":
    #WidgetRestricciones().run()
    #WidgetFuncionObjetivo().run()
    #WidgetSolucion().run()
    #WidgetTablaIteraciones().run()
    pass