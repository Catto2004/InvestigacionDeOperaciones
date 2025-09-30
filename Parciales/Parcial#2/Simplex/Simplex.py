# Simplex/Simplex.py
# Implementación del método Simplex para Programación Lineal

from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import SimplexTCSS
import MicroModulos
import EjerciciosDemo

class SimplexApp(Screen):
    CSS = SimplexTCSS.CSS
    BINDINGS = [
        ("b", "back", "Volver al menú"),
        ("r", "reset", "Resetear"),
        ("q", "quit", "Salir")
    ]