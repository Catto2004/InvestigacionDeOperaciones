
# TestPlotter.py
from Plotter import DibujarRestricciones
from Solver import resolverPL

funcion = "x + y"
restricciones = ["x+3y<=26", "4x+3y<=44", "2x+3y<=28", "x>=0", "y>=0"]

resultado = resolverPL(funcion, restricciones, modo="Max")
print(f"Estado: {resultado['estado']}")
print(f"x = {resultado['x']:.2f}, y = {resultado['y']:.2f}, z = {resultado['z']:.2f}")
DibujarRestricciones(funcion, restricciones, modo="Max")

input("Presione Enter para salir...")