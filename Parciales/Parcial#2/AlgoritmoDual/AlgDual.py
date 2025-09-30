# AlgoritmoDual/AlgDual.py
# Implementación del Algoritmo Dual para Programación Lineal
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

# Conexión al directorio padre para pruebas individuales
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import AlgDualTCSS
import MicroModulos
import EjerciciosDemo

class AlgDualApp(Screen):
    CSS = AlgDualTCSS.CSS
    BINDINGS = [
        ("b", "back", "Volver al menú"),
        ("r", "reset", "Resetear"),
        ("q", "quit", "Salir")
    ]