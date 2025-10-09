# MicroModulos.py
# Módulo que agrupa las importaciones necesarias para los modulos de la aplicación

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Input, Button, Static, Label, DataTable
from textual.reactive import reactive

from rich.text import Text

import Parser

# ############### Widget "Restricciones"
class WidgetRestricciones(Container):
    """Widget para ingresar, mostrar y eliminar restricciones."""

    """-> ¿Cómo funciona?
    - El usuario ingresa una restricción en el Input y presiona Enter.
    - También puede escribir "-<indice>" (por ejemplo "-2") para eliminar la restricción que tenga ese índice.
    - Las restricciones válidas se agregan a la lista y se muestran numeradas.
    - Se puede obtener la lista de restricciones con GetRestricciones().
    - Se puede resetear el widget a su estado inicial con Reset().
    - Se valida cada restricción al ingresarla usando Parser.Parsear().
    """

    # Lista reactiva de restricciones
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Restricciones = []

    # Composición del widget
    def compose(self):
        with Vertical(id="WidgetRestricciones"):
            yield Label("Restricciones:", id="TituloRestricciones")
            yield Input(placeholder="Ingrese una restricción o '-N' para eliminar...", id="InputRestriccion")
            yield Static("(Sin restricciones)", id="TablaRestricciones")

    # Evento al enviar el input
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "InputRestriccion":
            nueva = event.value.strip()
            event.input.value = ""  # limpiar el input

            # Intentar eliminar una restricción si se ingresa "-<indice>""
            if nueva.startswith("-") and nueva[1:].isdigit():
                indice = int(nueva[1:]) - 1
                if 0 <= indice < len(self.Restricciones):
                    eliminada = self.Restricciones.pop(indice)
                    self.notify(f"🗑️ Restricción eliminada: {eliminada}", severity="information")
                    self.ActualizarTabla()
                else:
                    self.notify(f"⚠ No existe la restricción #{indice+1}", severity="warning")
                return

            # De lo contrario, intentar agregar la nueva restricción
            try:
                Parser.Parsear(nueva)  # validar
            except ValueError as e:
                self.notify(f"⚠ Restricción inválida: {e}", severity="error")
                return

            self.Restricciones.append(nueva)
            self.ActualizarTabla()

    # Actualiza la tabla de restricciones mostrada  
    def ActualizarTabla(self):
        if self.Restricciones:
            contenido = "\n".join(f"{i+1}. {r}" for i, r in enumerate(self.Restricciones))
        else:
            contenido = ""
        self.query_one("#TablaRestricciones", Static).update(contenido)

    # Devuelve la lista actual de restricciones
    def GetRestricciones(self):
        return self.Restricciones

    # Reinicia el widget a estado inicial
    def Reset(self):
        self.Restricciones = []
        self.query_one("#InputRestriccion", Input).value = ""
        self.ActualizarTabla()


# ############### Widget "Función Objetivo"
class WidgetFuncionObjetivo(Container):
    """Widget para ingresar y mostrar la función objetivo y el modo (Max/Min)."""

    """-> ¿Cómo funciona?
    - El usuario ingresa la función objetivo en el Input y selecciona el modo (Max/Min).
    - La función objetivo se valida al ingresarla usando Parser.Parsear().
    - Se puede obtener la función objetivo y el modo con GetFuncionObjetivo().
    - Se puede reiniciar el widget a su estado inicial con Reset().
    """

    modo = reactive("Max")
    funcion_objetivo = reactive("")

    # Composición del widget
    def compose(self):
        with Container(id="WidgetFuncionObjetivo"):
            yield Label("Función objetivo:", id="TituloFunObj")
            with Horizontal(id="ControlesFunObj"):
                yield Button(self.modo, id="MaxMin")
                yield Input(placeholder="3x1 + 4x2 + 3x3", id="InputFunObj")

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
    
    # Reiniciar a estado inicial
    def Reset(self):
        self.modo = "Max"
        self.funcion_objetivo = ""
        self.query_one("#MaxMin", Button).label = self.modo
        self.query_one("#InputFunObj", Input).value = ""


# ############### Widget "Solución"
class WidgetSolucion(Container):
    """Widget para mostrar la solución del problema."""

    """-> ¿Cómo funciona?
    - ActualizarSolucion(nuevo_resultado): actualiza la vista con el nuevo resultado.
    - Reset(): reinicia la solución a estado inicial.
    - GetSolucion(): devuelve el estado actual como dict (por si se necesita).
    """

    Resultado = reactive({"Estado": "Esperando", "Z": 0.0})

    # Composición del widget
    def compose(self):
        with Vertical(id="WidgetSolucion"):
            yield Label("Solución:", id="TituloSolucion")
            yield Label(f"Estado: {self.Resultado['Estado']}", id="SolucionEstado")
            TablaSolucion = DataTable(id="TablaSolucion")
            TablaSolucion.add_columns("Variable", "Valor")
            yield TablaSolucion

    # Actualiza la solución mostrada
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

    def Reset(self):
        """Reinicia la solución a estado inicial."""
        self.ActualizarSolucion({"Estado": "Esperando", "Z": 0.0})

    def GetSolucion(self):
        """Devuelve el estado actual como dict (por si se necesita)."""
        return self.Resultado


# ############### Widget "Tabla de Iteraciones" 
class WidgetTablaIteraciones(Static):
    """Muestra las iteraciones del método simplex en formato tabular."""

    def compose(self):
        yield Static("Sin iteraciones aún.", id="TablaIteraciones")

    def ActualizarIteracion(self, snapshot: dict, iteracion: int, fase: int, z_valor: float):
        """Recibe snapshot del solver y muestra tabla formateada."""
        if not snapshot:
            self.query_one("#TablaIteraciones", Static).update("❌ No hay datos de iteración.")
            return

        nombres = snapshot["var_names"] + ["RHS"]
        filas = snapshot["rows"]
        z_row = snapshot["z_row"]

        # Encabezado
        lineas = []
        lineas.append(f"────────────────────────────────────────────")
        lineas.append(f" Iteración {iteracion}   (Fase {fase})")
        lineas.append(f"────────────────────────────────────────────")
        lineas.append(" | ".join(f"{h:>6}" for h in ["Base"] + nombres))
        lineas.append("-" * (8 * (len(nombres) + 1)))

        # Filas del tableau
        for f in filas:
            row = [f"{f['base_name']:>6}"]
            for v in f["coeffs"]:
                row.append(f"{v:>6.3f}")
            row.append(f"{f['rhs']:>6.3f}")
            lineas.append(" | ".join(row))

        # Fila Z
        lineas.append("-" * (8 * (len(nombres) + 1)))
        z_fila = [f"{z_row['base_name']:>6}"]
        for v in z_row["coeffs"]:
            z_fila.append(f"{v:>6.3f}")
        z_fila.append(f"{z_row['rhs']:>6.3f}")
        lineas.append(" | ".join(z_fila))

        texto = "\n".join(lineas)

        # Mostrar en pantalla
        self.query_one("#TablaIteraciones", Static).update(Text(texto))

    def Reset(self):
        self.query_one("#TablaIteraciones", Static).update("Sin iteraciones aún.")

    def GetIteracion(self):
        """Devuelve el estado actual como dict (por si se necesita)."""
        return self.query_one("#TablaIteraciones", Static).renderable
    

