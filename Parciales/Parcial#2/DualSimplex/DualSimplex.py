# DualSimplex/DualSimplex.py
# Implementación del Algoritmo Dual para Programación Lineal
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, Label, TextArea
from textual.containers import Vertical, Horizontal, Container
from textual.screen import Screen

# Conexión al directorio padre (Parcial#2) para pruebas individuales
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from . import DualSimplexTCSS
from . import SolverDualSimplex
from Dual.Dual import DualConversor

import MicroModulos
import EjerciciosDemo

class DualSimplexApp(Screen):
    # ################ Configuración de la App ################
    CSS = DualSimplexTCSS.CSS
    BINDINGS = [
        ("^b", "back", "Volver al menú"),
        ("^r", "reset", "Resetear"),
        ("^c", "convert", "Convertir a dual"),
        ("^i", "iterate", "Iterar"),
        ("^d", "demo", "Cargar demo"),
    ]
    TITLE = "Parcial #2 / Algoritmo Dual Simplex."

    # ################ Variables del problema ################
    Problema = {"modo": "Min", "funcion_objetivo": "", "restricciones": []}   # Problema actual
    Iteraciones = [] # Iteraciones del proceso
    Solucion = {}    # Solución final
    Dual = {}        # Problema dual convertido
    EsDual = False   # Indica si el problema actual es dual
    Solver = None    # Instancia del solver
    DualConversor = None  # Instancia del conversor


    # ################ Inicialización del solver ################
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Solver = SolverDualSimplex.SolverDualSimplex()


    # ################ Composición de la App ################
    def compose(self) -> ComposeResult:
        """Define la estructura de la interfaz."""

        yield Header()
        yield Footer()

        # Panel principal con dos columnas
        with Horizontal(id="PanelPrincipal"):
            # Panel izquierdo con inputs y solución
            with Vertical(id="PanelIzquierdo"):
                yield MicroModulos.WidgetFuncionObjetivo(id="FuncionObjetivo")
                yield MicroModulos.WidgetRestricciones(id="Restricciones")
                yield MicroModulos.WidgetSolucion(id="Solucion")

            # Panel derecho con tabla de iteraciones
            with Vertical(id="PanelDerecho"):
                # Contenedor para el resultado del Problema Dual
                with Vertical(id="ContenedorResultadoDual"):
                    yield Label("Problema Dual:", id="TituloConversionDual")
                    yield TextArea("Esperando...", id="ResultadoDual", read_only=True)
                # Contenedor para el resultado del Problema Dual
                with Vertical(id="ContenedorIteraciones"):
                    yield Label("Tabla de Iteraciones:", id="TituloIteraciones")
                    yield MicroModulos.WidgetTablaIteraciones(id="TablaIteraciones")


    # ################ Acciones (atajos de teclado) ################
    def action_back(self):
        """Vuelve al menú principal."""

        self.app.pop_screen()


    def action_reset(self):
        """Reinicia la interfaz y las variables del problema."""

        # Reinicia los widgets
        self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo).Reset()
        self.query_one("#Restricciones", MicroModulos.WidgetRestricciones).Reset()
        self.query_one("#Solucion", MicroModulos.WidgetSolucion).Reset()
        self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones).Reset()
        self.query_one("#ResultadoDual", TextArea).value = "Esperando..."
        # Reinicia las variables del problema
        self.Solver = None
        self.Problema = {"modo": "Min", "funcion_objetivo": "", "restricciones": []}
        self.Iteraciones = []
        self.Solucion = {}
        self.Dual = {}
        self.EsDual = False
        # Notifica al usuario
        self.notify("♻️ Interfaz reiniciada.", severity="information")


    def action_iterate(self):
        """Ejecuta una iteración del método Dual Simplex sobre el problema dual ya convertido."""
        try:
            # 1️⃣ Verificar que ya se haya hecho la conversión
            if not self.EsDual or not hasattr(self, "ResultadoDual") or not self.ResultadoDual:
                self.notify("⚠ Debe convertir primero el problema a su forma dual (Ctrl+C).", severity="warning")
                return

            # Obtener widgets necesarios
            widget_iter = self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones)
            widget_sol = self.query_one("#Solucion", MicroModulos.WidgetSolucion)
            widget_dual = self.query_one("#ResultadoDual", TextArea)

            dual_data = self.ResultadoDual

            # 2️⃣ Inicializar solver dual si aún no está listo
            if self.Solver is None or self.Solver.A is None:
                from DualSimplex.SolverDualSimplex import DualSimplexSolver
                self.Solver = DualSimplexSolver()

                # Limpieza de la FO (el conversor incluye "Min W =" o "Max W =")
                fo_limpia = dual_data["funcion_objetivo"]
                fo_limpia = fo_limpia.replace("Max W =", "").replace("Min W =", "").strip()

                # Inicializar
                self.Solver.initialize(
                    dual_data["tipo_dual"],
                    fo_limpia,
                    dual_data["restricciones"]
                )

                # Advertencia si el problema no tiene optimalidad dual inicial
                if not self.Solver.check_dual_feasibility():
                    self.notify("⚠ El problema dual no tiene optimalidad dual inicial. Puede no converger.", severity="warning")

            # 3️⃣ Ejecutar iteración
            info = self.Solver.iterate_one()

            # 4️⃣ Procesar resultados
            if info["status"] == "continue":
                snapshot = info["snapshot"]
                widget_iter.ActualizarIteracion(snapshot, info["iteration"], self.Solver.phase, info["Z"])
                widget_sol.ActualizarSolucion(self.Solver.get_solution())
                self.notify(f"➡ Iteración {info['iteration']} completada correctamente.", severity="information")

            elif info["status"] == "optimal":
                snapshot = info.get("snapshot")
                if snapshot:
                    widget_iter.ActualizarIteracion(snapshot, info["iteration"], self.Solver.phase, info["Z"])
                widget_sol.ActualizarSolucion(self.Solver.get_solution())
                self.notify("🎯 Solución óptima alcanzada (Dual Simplex).", severity="success")

            elif info["status"] == "infeasible":
                self.notify("❌ El problema dual no tiene solución factible.", severity="error")

            elif info["status"] == "dual_infeasible":
                self.notify("⚠ El problema no cumple con optimalidad dual inicial.", severity="warning")

        except Exception as e:
            self.notify(f"⚠ Error durante la iteración: {e}", severity="error")


   # Acción: Convertir el problema primal a dual
    def action_convert(self):
        """Convierte el problema primal actual a su forma dual y la muestra en pantalla."""
        try:
            widgetFO = self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo)
            widgetRest = self.query_one("#Restricciones", MicroModulos.WidgetRestricciones)
            widgetOutput = self.query_one("#ResultadoDual", TextArea)

            funcion, modo = widgetFO.GetFuncionObjetivo()
            restricciones = widgetRest.GetRestricciones()

            if not funcion or not restricciones:
                self.notify("⚠ Debe ingresar una función objetivo y al menos una restricción.", severity="warning")
                return

            # Guardar el problema primal
            # Cambia el estado del estado Dual
            self.EsDual = True
            self.Problema = {
                "modo": modo,
                "funcion_objetivo": funcion,
                "restricciones": restricciones
            }

            # Crear instancia del conversor y convertir
            conversor = DualConversor.DualConversor()
            dual = conversor.Convertir(funcion, restricciones, tipo_primal=modo.upper())

            # Guardar resultado dual globalmente
            self.Dual = dual
            self.EsDual = True

            # Construir texto de salida
            texto_dual = (
                f"Modo: {dual['tipo_dual']}\n\n"
                f"Función Objetivo Dual:\n  {dual['funcion_objetivo']}\n\n"
                f"Restricciones:\n"
                + "\n".join(f"  {r}" for r in dual['restricciones'])
            )

            if "condiciones" in dual and dual["condiciones"]:
                texto_dual += "\n\nCondiciones de signo:\n" + "\n".join(f"  {c}" for c in dual["condiciones"])

            # Mostrar resultado en la interfaz
            widgetOutput.text = texto_dual

            self.notify("✅ Conversión completada correctamente. Use Ctrl+I para iterar el dual.", severity="information")

        except Exception as e:
            self.notify(f"⚠ Error al convertir: {e}", severity="error")

    def action_demo(self):
        """Carga un ejercicio de demostración, lo convierte a dual y muestra el tableau inicial."""
        try:
            # Widgets
            widget_fo = self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo)
            widget_restr = self.query_one("#Restricciones", MicroModulos.WidgetRestricciones)
            widget_iter = self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones)
            widget_sol = self.query_one("#Solucion", MicroModulos.WidgetSolucion)
            widget_dual = self.query_one("#ResultadoDual", TextArea)

            # Reiniciar visualmente
            widget_fo.Reset()
            widget_restr.Reset()
            widget_iter.Reset()
            widget_sol.Reset()
            widget_dual.value = "Esperando..."

            # 1️⃣ Ejemplo base (problema primal)
            modo = "Max"
            funcion = "300x1 + 400x2"
            restricciones = [
                "3x1 + 3x2 <= 120",
                "3x1 + 6x2 <= 180",
                "x1 >= 0",
                "x2 >= 0"
            ]

            # 2️⃣ Asignar a los widgets visuales
            widget_fo.query_one("#InputFunObj").value = funcion
            widget_fo.funcion_objetivo = funcion
            widget_fo.modo = modo
            widget_fo.query_one("#MaxMin").label = modo

            widget_restr.Restricciones = list(restricciones)
            widget_restr.ActualizarTabla()

            # Guardar el problema primal internamente
            self.Problema = {"modo": modo, "funcion_objetivo": funcion, "restricciones": restricciones}

            # 3️⃣ Convertir a dual automáticamente
            conversor = DualConversor.DualConversor()
            self.ResultadoDual = conversor.Convertir(funcion, restricciones, tipo_primal=modo.upper())
            self.EsDual = True

            # Mostrar el problema dual en pantalla
            texto_dual = (
                f"Modo: {self.ResultadoDual['tipo_dual']}\n\n"
                f"Función Objetivo Dual:\n  {self.ResultadoDual['funcion_objetivo']}\n\n"
                f"Restricciones:\n" + "\n".join(f"  {r}" for r in self.ResultadoDual['restricciones']) + "\n\n"
                f"Condiciones:\n" + "\n".join(f"  {c}" for c in self.ResultadoDual['condiciones'])
            )
            widget_dual.text = texto_dual

            # 4️⃣ Inicializar solver dual
            self.Solver = SolverDualSimplex.SolverDualSimplex()

            fo_limpia = self.ResultadoDual["funcion_objetivo"].replace("Max W =", "").replace("Min W =", "").strip()
            self.Solver.initialize(self.ResultadoDual["tipo_dual"], fo_limpia, self.ResultadoDual["restricciones"])

            # 5️⃣ Mostrar tableau inicial
            snapshot = self.Solver.get_tableau_display()
            widget_iter.ActualizarIteracion(snapshot, iteracion=0, fase=self.Solver.phase, z_valor=0)

            self.notify("✅ Problema de demostración Dual Simplex cargado y convertido correctamente.", severity="information")

        except Exception as e:
            self.notify(f"⚠ Error al cargar demo: {e}", severity="error")
