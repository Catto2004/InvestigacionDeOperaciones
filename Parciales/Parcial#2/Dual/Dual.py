# Dual/Dual.py
# Implementación del método Dual para Programación Lineal
from textual.widgets import Header, Footer, Label, TextArea
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

# Conexión al directorio padre para pruebas individuales
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from . import DualTCSS
from . import DualConversor
import MicroModulos
import EjerciciosDemo

class DualApp(Screen):

    # ################ Variables de la interfaz ################
    CSS = DualTCSS.CSS
    BINDINGS = [
        ("^b", "back", "Volver al menú"),
        ("^r", "reset", "Resetear"),
        ("^c", "solve", "Convertir")
    ]
    TITLE = "Parcial #2 / Conversor de PL Prima -> Dual"

    # ################ Variables del problema ################
    def _on_mount(self, event):
        self.Problema = {"modo": "Max", "funcion_objetivo": "", "restricciones": []}   # Problema actual
        self.ResultadoDual = {"modo": "", "funcion_objetivo": "", "restricciones": []} # Problema dual resultante

    # Composición de la interfaz
    def compose(self):
        yield Header()
        yield Footer()

        with Horizontal(id="PanelPrincipal"):
            # Panel izquierdo: Inputs del problema
            with Vertical(id="PanelIzquierdo"):
                yield MicroModulos.WidgetFuncionObjetivo(id="FuncionObjetivo")
                yield MicroModulos.WidgetRestricciones(id="Restricciones")
            
            # Panel derecho: Resultados
            with Vertical(id="PanelDerecho"):
                yield Label("Resultado de la conversión:", id="TituloSolucionDual")
                yield TextArea("Esperando...", id="ResultadoDual", read_only=True)
    
    # Acción: Volver al menú principal
    def action_back(self):
        self.app.pop_screen()

    # Acción: Resetear la interfaz
    def action_reset(self):
        self.Problema = {"modo": "Max", "funcion_objetivo": "", "restricciones": []}
        self.ResultadoDual = {"modo": "", "funcion_objetivo": "", "restricciones": []}
        self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo).Reset()
        self.query_one("#Restricciones", MicroModulos.WidgetRestricciones).Reset()
        self.query_one("#ResultadoDual", TextArea).text = "Esperando..."

    # Acción: Convertir el problema primal a dual
    def action_solve(self):
        try:
            # Obtener widgets
            widgetFO = self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo)
            widgetRest = self.query_one("#Restricciones", MicroModulos.WidgetRestricciones)
            widgetOutput = self.query_one("#ResultadoDual", TextArea)

            # Obtener datos del usuario
            funcion, modo = widgetFO.GetFuncionObjetivo()
            restricciones = widgetRest.GetRestricciones()

            if not funcion or not restricciones:
                self.notify("⚠ Debe ingresar una función objetivo y al menos una restricción.", severity="warning")
                return

            # Guardar el problema primal
            self.Problema = {
                "modo": modo,
                "funcion_objetivo": funcion,
                "restricciones": restricciones
            }

            # Crear instancia del conversor y convertir
            conversor = DualConversor.DualConversor()
            self.ResultadoDual = conversor.Convertir(
                self.Problema["funcion_objetivo"],
                self.Problema["restricciones"],
                self.Problema["modo"]
            )

            # Construir texto para mostrar
            texto_dual = (
                f"Modo: {self.ResultadoDual['tipo_dual']}\n\n"
                f"Función Objetivo Dual:\n  {self.ResultadoDual['funcion_objetivo']}\n\n"
                f"Restricciones:\n"
                + "\n".join(f"  {r}" for r in self.ResultadoDual['restricciones'])
            )

            if "condiciones" in self.ResultadoDual and self.ResultadoDual["condiciones"]:
                texto_dual += "\n\nCondiciones de signo:\n" + "\n".join(f"  {c}" for c in self.ResultadoDual["condiciones"])

            # Mostrar en el TextArea
            widgetOutput.text = texto_dual

            # Notificación de éxito
            self.notify("✅ Conversión completada correctamente.", severity="information")

        except Exception as e:
            self.notify(f"⚠ Error al convertir: {e}", severity="error")

