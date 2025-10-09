# Simplex/Simplex.py
# Pantalla principal del Método Simplex paso a paso
# Compatible con el estilo general del proyecto y con SolverSimplex.py

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer
from textual.screen import Screen

import MicroModulos
from . import SimplexTCSS
from . import SolverSimplex

class SimplexApp(Screen):
    """Pantalla interactiva del Método Simplex paso a paso."""

    # ==================== Variables de la interfaz ====================
    CSS = SimplexTCSS.CSS  # cargar el CSS desde SimplexTCSS.py
    BINDINGS = [
        ("^b", "back", "Volver al menú"),
        ("^r", "reset", "Resetear"),
        ("^i", "iterate", "Iterar"),
        ("^d", "demo", "Cargar demo"),
    ]
    TITLE = "Parcial #2 / Algoritmo Simplex"

    # ==================== Variables del problema ====================
    Problema = {"modo": "Max", "funcion_objetivo": "", "restricciones": []}
    Iteraciones = []
    Solucion = {}

    # Instancia del solver
    Solver = None

    # ==================== Inicialización del solver ====================
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Solver = SolverSimplex.SimplexSolver()

    # ==================== Composición de la interfaz ====================
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with Horizontal(id="PanelPrincipal"):
            with Vertical(id="PanelIzquierdo"):
                yield MicroModulos.WidgetFuncionObjetivo(id="FuncionObjetivo")
                yield MicroModulos.WidgetRestricciones(id="Restricciones")
                yield MicroModulos.WidgetSolucion(id="Solucion")

            with Vertical(id="PanelDerecho"):
                yield MicroModulos.WidgetTablaIteraciones(id="TablaIteraciones")

    # ==================== Acciones (atajos de teclado) ====================

    def action_back(self):
        """Volver al menú principal."""
        self.app.pop_screen()

    def action_reset(self):
        """Reinicia todos los widgets y el solver."""
        self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo).Reset()
        self.query_one("#Restricciones", MicroModulos.WidgetRestricciones).Reset()
        self.query_one("#Solucion", MicroModulos.WidgetSolucion).Reset()
        self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones).Reset()
        self.Solver = None
        self.Problema = {"modo": "Max", "funcion_objetivo": "", "restricciones": []}
        self.notify("♻️ Interfaz reiniciada correctamente.", severity="information")

    def action_iterate(self):
        """Ejecuta una iteración del método Simplex y actualiza el tableau visual."""
        try:
            # 1️⃣ Inicialización segura del solver
            if self.Solver is None:
                self.Solver = SolverSimplex.SimplexSolver()

            if self.Solver.A is None:
                fo_widget = self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo)
                restr_widget = self.query_one("#Restricciones", MicroModulos.WidgetRestricciones)

                funcion, modo = fo_widget.GetFuncionObjetivo()
                restricciones = restr_widget.GetRestricciones()

                if not funcion or funcion.strip() == "":
                    self.notify("⚠ Debe ingresar la función objetivo antes de iterar.", severity="warning")
                    return

                # Inicializa el solver con los datos
                self.Solver.initialize(modo, funcion, restricciones)

        except Exception as e:
            self.notify(f"⚠ Error durante la inicialización: {e}", severity="error")
            return

        # 2️⃣ Ejecutar una iteración del método
        try:
            info = self.Solver.iterate_one()
        except Exception as e:
            self.notify(f"⚠ Error durante la iteración: {e}", severity="error")
            return

        # 3️⃣ Mostrar el resultado en el widget de iteraciones
        try:
            tabla_iter = self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones)
            sol_widget = self.query_one("#Solucion", MicroModulos.WidgetSolucion)

            # Si hay snapshot del tableau, mostrarlo
            if "snapshot" in info and info["snapshot"]:
                tabla_iter.ActualizarIteracion(
                    snapshot=info["snapshot"],
                    iteracion=self.Solver.iteration,
                    fase=self.Solver.phase,
                    z_valor=info.get("Z", 0.0)
                )

            # Actualizar panel de solución actual
            if info.get("status") in ("continue", "optimal"):
                sol_widget.ActualizarSolucion(self.Solver.get_solution())

            # Estado del solver
            status = info.get("status", "")
            if status == "continue":
                self.notify(f"➡️ Iteración {self.Solver.iteration} completada.", severity="information")
            elif status == "optimal":
                self.notify("🎯 Solución óptima alcanzada.", severity="success")
            elif status == "unbounded":
                self.notify("⚠ El problema es ilimitado.", severity="error")
            elif status == "infeasible":
                self.notify("❌ El problema no tiene solución factible.", severity="error")
            elif status == "phase1_to_phase2":
                self.notify("🔄 Fin de Fase I → iniciando Fase II...", severity="information")

        except Exception as e:
            self.notify(f"⚠ Error procesando los resultados: {e}", severity="error")


    def action_demo(self):
        """Carga un ejercicio de demostración y muestra el tableau inicial."""
        try:
            # Widgets
            widget_fo = self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo)
            widget_restr = self.query_one("#Restricciones", MicroModulos.WidgetRestricciones)
            widget_iter = self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones)
            widget_sol = self.query_one("#Solucion", MicroModulos.WidgetSolucion)

            # Reiniciar visualmente
            widget_fo.Reset()
            widget_restr.Reset()
            widget_iter.Reset()
            widget_sol.Reset()

            # Cargar ejemplo clásico
            modo = "Max"
            funcion = "300x1 + 400x2"
            restricciones = [
                "3x1 + 3x2 <= 120",
                "3x1 + 6x2 <= 180",
                "x1 >= 0",
                "x2 >= 0"
            ]

            # Asignar a los widgets
            widget_fo.query_one("#InputFunObj").value = funcion
            widget_fo.funcion_objetivo = funcion
            widget_fo.modo = modo
            widget_fo.query_one("#MaxMin").label = modo

            widget_restr.Restricciones = list(restricciones)
            widget_restr.ActualizarTabla()

            # Guardar problema interno
            self.Problema = {"modo": modo, "funcion_objetivo": funcion, "restricciones": restricciones}

            # Inicializar solver con los datos demo
            self.Solver = SolverSimplex.SimplexSolver()
            self.Solver.initialize(modo, funcion, restricciones)

            # Mostrar el tableau inicial (iteración 0)
            snapshot = self.Solver.get_tableau_display()
            widget_iter.ActualizarIteracion(snapshot, iteracion=0, fase=self.Solver.phase, z_valor=0)

            self.notify("✅ Problema de demostración cargado correctamente.", severity="information")

        except Exception as e:
            self.notify(f"⚠ Error al cargar demo: {e}", severity="error")


    # ==================== Inicio automático ====================

    def on_mount(self):
        """Preparar la interfaz al cargar."""

