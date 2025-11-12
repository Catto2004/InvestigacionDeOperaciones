# main.py

from optimizer import Optimizer
from utils import parse_constraints, parse_objective_function

import os

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(Panel.fit("[bold cyan]Parcial 2 - Problemas de PL by Carlos Laverde && Juan Benjumea[/bold cyan]", style="blue"))
    console.print("[bold]Métodos disponibles:[/bold]")
    console.print("  [1] Simplex\n  [2] Dual\n  [3] Dual Simplex\n", style="yellow")

    # Selección de método
    while True:
        metodo = Prompt.ask("Seleccione el método (1, 2 o 3)", choices=["1","2","3"], default="1")
        if metodo in ['1', '2', '3']:
            if metodo == '1':
                metodo = "simplex"
            elif metodo == '2':
                metodo = "dual"
            else:
                metodo = "dualsimplex"  # Dual Simplex
            break

    # Preguntar si maximizar o minimizar
    objetivo = Prompt.ask("¿Desea maximizar o minimizar la función objetivo?", choices=["max","min"], default="max")

    # Input función objetivo
    objective_function = Prompt.ask("Introduzca la función objetivo (ej: '3x1 + 2x2')")
    try:
        objective_function = parse_objective_function(objective_function)
    except ValueError as e:
        console.print(f"[red]Error al parsear la función objetivo: {e}[/red]")
        return

    # Input restricciones una por una (acepta ';' para múltiples en una sola línea)
    constraints = []
    console.print("\n[bold]Ingrese restricciones una por línea. Para terminar deje vacío y presione enter.[/bold]")
    console.print("[dim]Ejemplos: x1 + 2x2 <= 10  |  x1 >= 0  |  x1 + x2 = 5[/dim]")

    while True:
        restriccion = Prompt.ask("Introduzca una restricción (o deje vacío para terminar)").strip()
        if not restriccion:
            break
        try:
            parsed = parse_constraints(restriccion)
            constraints.extend(parsed)
        except ValueError as e:
            console.print(f"[red]Restricción inválida: {e}[/red]")
            continue

    if not objective_function or not constraints:
        console.print("[red]Error: entrada no válida. Revise la función objetivo y las restricciones.[/red]")
        return

    # Crear el optimizador
    optimizer = Optimizer(objective_function, constraints, objetivo, verbose=True)

    # Resolver según el método seleccionado
    if metodo == "simplex":
        result = optimizer.solve_simplex()
    elif metodo == "dual":
        result = optimizer.solve_dual()
    else:  # Dual Simplex
        A, b, c = optimizer._parse_problem()
        tableau = optimizer._create_tableau_for_dual(A, b, c)
        result = optimizer._dual_simplex(tableau, c, A, b)

    if result is not None and isinstance(result, tuple):
        x, z, status = result
        console.print(Panel.fit(f"[green]Y {status}[/green]\n\n[bold]Z[/bold] = {optimizer._format_num(z)}", title="Solución", style="magenta"))
    else:
        # Algunos métodos (p.ej. solve_dual) retornan (None, None, mensaje)
        if isinstance(result, tuple) and result[2]:
            console.print(Panel.fit(f"[yellow]{result[2]}[/yellow]", title="Info", style="yellow"))
        else:
            console.print(Panel.fit("[red]!!! No se encontró una solución factible.[/red]", style="red"))

if __name__ == "__main__":
    main()
