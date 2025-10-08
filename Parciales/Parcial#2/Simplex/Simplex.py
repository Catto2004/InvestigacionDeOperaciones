# Simplex/Simplex.py
# Pantalla principal del Método Simplex paso a paso
# Compatible con el estilo general del proyecto y con SolverSimplex.py

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer
from textual.screen import Screen
from textual import on

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
        self.solver = SolverSimplex.SimplexSolver()

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
        """Ejecuta una iteración del método Simplex."""

        try:
            if self.solver.A is None:
                # Inicializar la primera vez
                fo_widget = self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo)
                restr_widget = self.query_one("#Restricciones", MicroModulos.WidgetRestricciones)

                funcion, modo = fo_widget.GetFuncionObjetivo()
                restricciones = restr_widget.GetRestricciones()

                self.solver.initialize(modo, funcion, restricciones)
                self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones).ConfigurarColumnas(
                    ["Base"] + self.solver.var_names + ["RHS"]
                )

            info = self.solver.iterate_one()
            self._mostrar_iteracion(info)

        except Exception as e:
            self.notify(f"⚠ Error durante la iteración: {e}", severity="error")

        if not self.Solver:
            self.notify("⚠ Primero debe inicializar el problema (Ctrl+D para demo o ingresar datos).", severity="warning")
            return

        try:
            if self.Solver.is_optimal():
                self.notify("✅ Solución óptima alcanzada.", severity="success")
                self.query_one("#Solucion", MicroModulos.WidgetSolucion).ActualizarSolucion(self.Solver.get_solution())
                return

            info = self.Solver.iterate_one()

            tabla_iter = self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones)
            sol_widget = self.query_one("#Solucion", MicroModulos.WidgetSolucion)

            if info["status"] == "continue":
                tabla_iter.AgregarIteracion([
                    info["iteration"],
                    f"{info['Z']:.2f}",
                    info["entering_name"],
                    info["leaving_name"],
                ])
                sol_widget.ActualizarSolucion(self.Solver.get_solution())

            elif info["status"] == "optimal":
                sol_widget.ActualizarSolucion(self.Solver.get_solution())
                self.notify("🎯 Solución óptima alcanzada.", severity="success")

            elif info["status"] == "unbounded":
                self.notify("⚠ El problema es ilimitado.", severity="error")

            elif info["status"] == "infeasible":
                self.notify("❌ El problema no tiene solución factible.", severity="error")

            elif info["status"] == "phase1_to_phase2":
                self.notify("🔄 Fin de Fase I: iniciando Fase II...", severity="information")

        except Exception as e:
            self.notify(f"⚠ Error durante la iteración: {e}", severity="error")

    def action_demo(self):
        """Carga un ejercicio de demostración."""
        try:
            widget_fo = self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo)
            widget_restr = self.query_one("#Restricciones", MicroModulos.WidgetRestricciones)
            widget_iter = self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones)
            widget_sol = self.query_one("#Solucion", MicroModulos.WidgetSolucion)

            widget_fo.Reset()
            widget_restr.Reset()
            widget_iter.Reset()
            widget_sol.Reset()

            # Cargar ejemplo
            modo = "Max"
            funcion = "3x1 + 5x2"
            restricciones = [
                "2x1 + x2 <= 8",
                "x1 + 2x2 <= 8",
                "x1 >= 0",
                "x2 >= 0"
            ]

            widget_fo.query_one("#InputFunObj").value = funcion
            widget_fo.modo = modo
            widget_fo.query_one("#MaxMin").label = modo
            for r in restricciones:
                widget_restr.Restricciones.append(r)
            widget_restr.ActualizarTabla()

            self.Problema = {"modo": modo, "funcion_objetivo": funcion, "restricciones": restricciones}

            # Inicializar solver
            self.Solver = SimplexSolver()
            self.Solver.initialize(modo, funcion, restricciones)

            widget_iter.ConfigurarColumnas(["Iteración", "Z", "Entrante", "Saliente"])
            self.notify("✅ Problema de demostración cargado correctamente.", severity="information")

        except Exception as e:
            self.notify(f"⚠ Error al cargar demo: {e}", severity="error")

    # ==================== Inicio automático ====================

    def on_mount(self):
        """Preparar la interfaz al cargar."""
        self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones).ConfigurarColumnas(
            ["Iteración", "Z", "Entrante", "Saliente"]
        )
        self.notify("🧮 Pantalla Simplex lista. Use Ctrl+D para demo o ingrese datos.", severity="information")
