# Simplex/Simplex.py
# Implementación del método Simplex para Programación Lineal

from textual.app import ComposeResult, App
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from . import SimplexTCSS
from . import SolverSimplex
from Parser import Parsear
import MicroModulos
import EjerciciosDemo


class SimplexApp(Screen):
    CSS = SimplexTCSS.CSS
    BINDINGS = [
        ("^b", "back", "Volver al menú"),
        ("^r", "reset", "Resetear"),
        ("^i", "iterate", "Iterar"),
        ("^s", "solve", "Resolver"),
        ("^d", "demo", "Cargar demo")
    ]

    # ################ Manejo de la interfaz ################

    # Composición de la interfaz
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

    # Definición de variables al iniciar la pantalla
    def on_mount(self) -> None:
        self.solver = None

    # #### Manejo de Acciones
    # Atajo para volver
    async def action_back(self):
        self.app.pop_screen()  # o regresar al menú principal

    # Atajo para resetear todo
    async def action_reset(self):
        # Llamar a reset en widgets
        self.query_one("#Restricciones", MicroModulos.WidgetRestricciones).Reset()
        self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo).Reset()
        self.query_one("#Solucion", MicroModulos.WidgetSolucion).Reset()
        self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones).Reset()

    # Atajo para iterar un paso   
    async def action_iterate(self):
        """Realiza un solo paso del simplex y actualiza la tabla de iteraciones."""
        # Obtener widgets
        widgetFO = self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo)
        widgetRest = self.query_one("#Restricciones", MicroModulos.WidgetRestricciones)
        widgetTabla = self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones)

        # Si no hay solver creado, crear uno desde los datos actuales
        if self.solver is None:
            try:
                fo_parsed, modo = widgetFO.GetFuncionObjetivo()   # supongo retorna (parsed, modo) o (string, modo)
            except Exception as e:
                self.notify("Función objetivo no válida o no ingresada.", severity="error")
                return
            try:
                restricciones = widgetRest.GetRestricciones()    # supongo retorna lista de strings
            except Exception:
                restricciones = []

            # aquí debes convertir funcion objetivo y restricciones parseadas a (c, A, b)
            try:
                c, A, b = self.ConstruirMatrices(fo_parsed, restricciones, modo)
            except Exception as e:
                self.notify(f"Error al parsear datos: {e}", severity="error")
                return

            # crear solver y configurar tabla en widget
            self.solver = SolverSimplex.SimplexSolver(c, A, b, modo=modo)
            # configurar columnas para mostrar: número de columnas en tabla simplex
            num_cols = self.solver.tabla.shape[1]
            columnas = [f"C{i}" for i in range(num_cols)]
            widgetTabla.ConfigurarColumnas(columnas)
            # mostrar tabla inicial (fila por fila)
            widgetTabla.Reset()
            for fila in self.solver.tabla:
                widgetTabla.AgregarIteracion([round(float(v), 6) for v in fila])

        # ejecutar un paso
        try:
            hizo_paso = self.solver.Paso()
        except Exception as e:
            self.notify(f"Error en iteración: {e}", severity="error")
            return

        if not hizo_paso:
            # ya era óptimo
            resultado = self.solver.ExtraerSolucion()
            # actualizar widget solucion (suponiendo método update_solucion espera dict con X1..)
            sol_widget = self.query_one("#Solucion", MicroModulos.WidgetSolucion)
            # normalizar a dict estilo X1..Xn y Z
            sol_dict = {"Estado": "Optimal"}
            for i, val in enumerate(resultado["x"], start=1):
                sol_dict[f"X{i}"] = float(val)
            sol_dict["Z"] = float(resultado["z"])
            sol_widget.ActualizarSolucion(sol_dict)
            self.notify("Solución óptima alcanzada.", severity="success")
            return

        # si se hizo pivoteo, añadir la nueva tabla como iteración
        for fila in self.solver.tabla:
            widgetTabla.AgregarIteracion([round(float(v), 6) for v in fila])

    # función interna para construir matrices c, A, b desde FO y restricciones parseadas
    def ConstruirMatrices(self, fo_str: str, restricciones_str: list, modo: str)-> tuple:
        """
        Convierte los strings de la función objetivo y restricciones
        en c, A, b listos para el solver simplex.
        """
        # Parsear función objetivo
        fo = Parsear(fo_str + "<=0")  # truco para usar el parser de restricciones
        c = fo["coef"]

        # Parsear restricciones
        A, b = [], []
        for restr_str in restricciones_str:
            restr = Parsear(restr_str)
            coefs = restr["coef"]
            const = restr["constante"]

            # Normalizar: si es >=, multiplicamos por -1
            if restr["operador"] == ">=":
                coefs = [-x for x in coefs]
                const = -const

            A.append(coefs)
            b.append(const)

            return c, A, b
        
    # función interna para construir matrices c, A, b desde FO y restricciones parseadas
    async def action_resolver(self):
        """Resuelve completamente el problema (iteraciones hasta óptimo)."""
        # si no hay solver creado, inicializar igual que en action_iterate
        if self.solver is None:
            await self.action_iterate()  # esto crea el solver y dibuja la tabla inicial
            if self.solver is None:
                return  # error al crear solver

        # ejecutar pasos hasta óptimo
        try:
            while not self.solver.Optimo():
                self.solver.Paso()
        except Exception as e:
            self.notify(f"Error durante resolución: {e}", severity="error")
            return

        # mostrar la solución final
        resultado = self.solver.ExtraerSolucion()
        sol_widget = self.query_one("#Solucion", MicroModulos.WidgetSolucion)
        sol_dict = {"Estado": "Optimal"}
        for i, val in enumerate(resultado["x"], start=1):
            sol_dict[f"X{i}"] = float(val)
        sol_dict["Z"] = float(resultado["z"])
        sol_widget.ActualizarSolucion(sol_dict)

        # actualizar tabla de iteraciones (limpio y vuelvo a volcar todas)
        widgetTabla = self.query_one("#TablaIteraciones", MicroModulos.WidgetTablaIteraciones)
        widgetTabla.Reset()
        for tabla in resultado["iteraciones"]:
            for fila in tabla:
                widgetTabla.AgregarIteracion([round(float(v), 6) for v in fila])

    # Atajo para cargar un ejercicio de demo
    async def action_demo(self):
        """Carga un ejercicio de demostración desde EjerciciosDemo.py"""
        try:
            # Escogemos el primer demo por defecto (puedes hacer que sea aleatorio o por índice)
            demo = EjerciciosDemo.EjerciciosDemo[0]

            # Widgets
            widgetFO = self.query_one("#FuncionObjetivo", MicroModulos.WidgetFuncionObjetivo)
            widgetRest = self.query_one("#Restricciones", MicroModulos.WidgetRestricciones)

            # Resetear primero
            widgetFO.Reset()
            widgetRest.Reset()

            # Cargar función objetivo y modo
            widgetFO.funcion_objetivo = demo["funcion_objetivo"]
            widgetFO.modo = demo["modo"]
            widgetFO.query_one("#MaxMin").label = demo["modo"]
            widgetFO.query_one("#InputFunObj").value = demo["funcion_objetivo"]

            # Cargar restricciones
            for restr in demo["restricciones"]:
                widgetRest.restricciones.append(restr)
            widgetRest.ActualizarTabla()

            self.notify("✅ Ejercicio demo cargado correctamente.", severity="information")

        except Exception as e:
            self.notify(f"⚠ Error al cargar demo: {e}", severity="error")


"""
if __name__ == "__main__":
    # Ejecutar la aplicación Simplex
    SimplexApp().run()
    pass
"""