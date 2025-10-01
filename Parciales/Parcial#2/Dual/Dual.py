# Dual/Dual.py
# Implementación del método Dual para Programación Lineal
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

# Conexión al directorio padre para pruebas individuales
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from . import DualTCSS
from . import SolverDual
import MicroModulos
import EjerciciosDemo

class DualApp(Screen):
    CSS = DualTCSS.CSS
    BINDINGS = [
        ("b", "back", "Volver al menú"),
        ("r", "reset", "Resetear"),
        ("q", "quit", "Salir")
    ]