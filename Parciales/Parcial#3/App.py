"""
Aplicación de Interfaz en Consola para Problemas de Transporte
Utiliza los tres métodos: Esquina Noroeste, Menor Costo y Vogel
"""
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, FloatPrompt
from rich.panel import Panel
from rich.text import Text
from EsquinaOeste import MetodoEsquinaNoroeste
from MenorCosto import MetodoMenorCosto
from MetodoVoguel import MetodoVogel

console = Console()


def leer_datos():
    """Lee los datos del problema de transporte desde la consola."""
    console.print("\n[bold cyan]═══ PROBLEMA DE TRANSPORTE ═══[/bold cyan]\n")
    
    # Leer dimensiones
    m = IntPrompt.ask("[cyan]Ingrese la cantidad de orígenes (M)[/cyan]")
    n = IntPrompt.ask("[cyan]Ingrese la cantidad de destinos (N)[/cyan]")
    
    console.print(f"\n[yellow]→ Se creará una tabla de {m} orígenes × {n} destinos[/yellow]\n")
    
    # Crear tabla inicial vacía
    tabla_inicial = Table(title="Tabla Inicial", 
                         title_style="bold cyan",
                         header_style="bold cyan",
                         border_style="cyan")
    
    # Agregar columnas
    tabla_inicial.add_column("#", style="cyan", justify="center")
    for j in range(n):
        tabla_inicial.add_column(f"Destino {j+1}", justify="center")
    tabla_inicial.add_column("Producción", style="bold cyan", justify="center")
    
    # Leer datos
    costos = []
    oferta = []
    
    console.print("[bold cyan]Ingrese los datos fila por fila:[/bold cyan]\n")
    
    for i in range(m):
        console.print(f"[yellow]═══ Origen {i+1} ═══[/yellow]")
        
        # Leer costos de esta fila
        fila_costos = []
        for j in range(n):
            costo = FloatPrompt.ask(f"  Costo hacia Destino {j+1}")
            fila_costos.append(costo)
        
        # Leer producción
        prod = FloatPrompt.ask(f"  [bold]Producción del Origen {i+1}[/bold]")
        
        costos.append(fila_costos)
        oferta.append(prod)
        
        # Agregar fila a la tabla
        fila_datos = [f"Origen {i+1}"] + [str(c) for c in fila_costos] + [f"[bold]{prod}[/bold]"]
        tabla_inicial.add_row(*fila_datos)
        
        console.print()
    
    # Leer demanda
    console.print("[yellow]═══ Demanda ═══[/yellow]")
    demanda = []
    fila_demanda = ["[bold]Demanda[/bold]"]
    for j in range(n):
        dem = FloatPrompt.ask(f"  Demanda del Destino {j+1}")
        demanda.append(dem)
        fila_demanda.append(f"[bold]{dem}[/bold]")
    fila_demanda.append("#")
    tabla_inicial.add_row(*fila_demanda)
    
    # Mostrar tabla inicial
    console.print()
    console.print(tabla_inicial)
    
    # Validar balance
    total_oferta = sum(oferta)
    total_demanda = sum(demanda)
    
    console.print()
    if abs(total_oferta - total_demanda) < 0.001:
        console.print(f"[green]✓ El problema está balanceado[/green]")
        console.print(f"  Total Producción: {total_oferta}")
        console.print(f"  Total Demanda: {total_demanda}")
    else:
        console.print(f"[red]✗ ADVERTENCIA: El problema NO está balanceado[/red]")
        console.print(f"  Total Producción: {total_oferta}")
        console.print(f"  Total Demanda: {total_demanda}")
        console.print(f"  Diferencia: {abs(total_oferta - total_demanda)}")
        console.print("[yellow]Los métodos podrían fallar si no está balanceado[/yellow]")
    
    return costos, oferta, demanda, m, n


def mostrar_solucion(nombre_metodo, asignacion, costo_total, costos, oferta, demanda, color):
    """Muestra la solución de un método en una tabla formateada."""
    # Convertir a lista si es numpy array
    import numpy as np
    if isinstance(asignacion, np.ndarray):
        asignacion = asignacion.tolist()
    
    m = len(asignacion)
    n = len(asignacion[0])
    
    # Crear tabla de solución
    tabla = Table(title=nombre_metodo, 
                 title_style=f"bold {color}",
                 header_style=f"bold {color}",
                 border_style=color)
    
    # Agregar columnas
    tabla.add_column("#", style=color, justify="center")
    for j in range(n):
        tabla.add_column(f"Destino {j+1}", justify="center")
    tabla.add_column("Producción", style=f"bold {color}", justify="center")
    
    # Agregar filas con asignaciones
    for i in range(m):
        fila_datos = [f"Origen {i+1}"]
        for j in range(n):
            if asignacion[i][j] > 0:
                # Mostrar asignación y costo
                fila_datos.append(f"[bold]{asignacion[i][j]:.1f}[/bold]\n({costos[i][j]:.1f})")
            else:
                fila_datos.append("─")
        fila_datos.append(f"[bold]{oferta[i]:.1f}[/bold]")
        tabla.add_row(*fila_datos)
    
    # Agregar fila de demanda
    fila_demanda = ["[bold]Demanda[/bold]"]
    for j in range(n):
        fila_demanda.append(f"[bold]{demanda[j]:.1f}[/bold]")
    fila_demanda.append("#")
    tabla.add_row(*fila_demanda)
    
    console.print()
    console.print(tabla)
    console.print(f"[{color}]Costo Total: {costo_total:.2f}[/{color}]\n")


def main():
    """Función principal de la aplicación."""
    # Banner de bienvenida
    console.print()
    console.print(Panel.fit(
        "[bold cyan]MÉTODOS DE SOLUCIÓN PARA PROBLEMAS DE TRANSPORTE[/bold cyan]\n" +
        "[white]• Método de la Esquina Noroeste[/white]\n" +
        "[white]• Método del Menor Costo[/white]\n" +
        "[white]• Método de Vogel (VAM)[/white]",
        border_style="cyan"
    ))
    
    # Leer datos del problema
    costos, oferta, demanda, m, n = leer_datos()
    
    console.print("\n[bold yellow]═══════════════════════════════════════[/bold yellow]")
    console.print("[bold yellow]        RESOLVIENDO PROBLEMA...        [/bold yellow]")
    console.print("[bold yellow]═══════════════════════════════════════[/bold yellow]\n")
    
    try:
        # Método 1: Esquina Noroeste (Verde)
        console.print("[bold green]▼ Método de la Esquina Noroeste[/bold green]")
        asignacion1, costo1 = MetodoEsquinaNoroeste(costos, oferta, demanda)
        mostrar_solucion(
            "MÉTODO DE LA ESQUINA NOROESTE",
            asignacion1,
            costo1,
            costos,
            oferta,
            demanda,
            "green"
        )
        
        # Método 2: Menor Costo (Amarillo)
        console.print("[bold yellow]▼ Método del Menor Costo[/bold yellow]")
        asignacion2, costo2 = MetodoMenorCosto(costos, oferta, demanda)
        mostrar_solucion(
            "MÉTODO DEL MENOR COSTO",
            asignacion2,
            costo2,
            costos,
            oferta,
            demanda,
            "yellow"
        )
        
        # Método 3: Vogel (Rojo)
        console.print("[bold red]▼ Método de Vogel (VAM)[/bold red]")
        asignacion3, costo3 = MetodoVogel(costos, oferta, demanda)
        mostrar_solucion(
            "MÉTODO DE VOGEL (VAM)",
            asignacion3,
            costo3,
            costos,
            oferta,
            demanda,
            "red"
        )
        
        # Resumen comparativo
        console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]")
        console.print("[bold cyan]           RESUMEN COMPARATIVO         [/bold cyan]")
        console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")
        
        tabla_comparacion = Table(title="Comparación de Costos", 
                                 title_style="bold magenta",
                                 header_style="bold magenta",
                                 border_style="magenta")
        tabla_comparacion.add_column("Método", style="bold")
        tabla_comparacion.add_column("Costo Total", justify="right")
        tabla_comparacion.add_column("Diferencia con Mejor", justify="right")
        
        costos_metodos = [
            ("Esquina Noroeste", costo1, "green"),
            ("Menor Costo", costo2, "yellow"),
            ("Vogel (VAM)", costo3, "red")
        ]
        
        mejor_costo = min(costo1, costo2, costo3)
        
        for nombre, costo, color in costos_metodos:
            diferencia = costo - mejor_costo
            if diferencia == 0:
                dif_str = "[bold green]★ ÓPTIMO ★[/bold green]"
            else:
                dif_str = f"+{diferencia:.2f}"
            tabla_comparacion.add_row(
                f"[{color}]{nombre}[/{color}]",
                f"[{color}]{costo:.2f}[/{color}]",
                dif_str
            )
        
        console.print(tabla_comparacion)
        console.print()
        
    except Exception as e:
        console.print(f"\n[bold red]ERROR: {str(e)}[/bold red]\n")
        return
    
    console.print("[bold green]✓ Proceso completado exitosamente[/bold green]\n")


if __name__ == "__main__":
    main()
