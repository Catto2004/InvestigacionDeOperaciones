# Investigación de Operaciones: Parcial #2.2: Simplex de Dos Fases by JDRB
import os
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()
os.system("cls")

def mostrar_tabla_iter(b_inv_A, x_B, reduced_full, var_names, basic_vars=None, z_val=None):
    """Imprime la tabla simplex en formato elegante usando Rich.
    - b_inv_A: matriz B^{-1} * A (m x n)
    - x_B: solución básica (vector de longitud m)
    - reduced_full: vector de reduced costs en orden de variables (longitud n)
    - var_names: lista de nombres de variables (longitud n)
    - basic_vars: lista de índices (en var_names) de variables básicas por fila. Si None, usa filas numeradas.
    - z_val: valor objetivo (float)
    """
    m = b_inv_A.shape[0]
    n = b_inv_A.shape[1]
    
    # Crear tabla con Rich
    table = Table(
        title="Tabla Simplex",
        box=box.ROUNDED,
        header_style="bold cyan",
        border_style="bright_blue"
    )
    
    # Agregar columna para las variables básicas
    table.add_column("Base", style="bold yellow", justify="center")
    
    # Agregar columnas para cada variable
    for var_name in var_names:
        table.add_column(var_name, justify="right", style="white")
    
    # Agregar columna de solución
    table.add_column("Sol", justify="right", style="bold green")
    
    # Agregar filas de restricciones
    for i in range(m):
        row_data = []
        
        # Etiqueta de variable básica
        if basic_vars is None:
            row_label = f"r{i+1}"
        else:
            row_label = var_names[basic_vars[i]]
        
        row_data.append(row_label)
        
        # Valores de la matriz B^{-1} * A
        for j in range(n):
            val = b_inv_A[i, j]
            if abs(val) < 1e-10:
                row_data.append("0")
            else:
                row_data.append(f"{val:.4f}")
        
        # Valor de la solución
        sol_val = x_B[i]
        if abs(sol_val) < 1e-10:
            row_data.append("0")
        else:
            row_data.append(f"{sol_val:.4f}")
        
        table.add_row(*row_data)
    
    # Agregar fila z (reduced costs)
    z_row = ["z"]
    for j in range(n):
        val = reduced_full[j] if j < len(reduced_full) else 0.0
        if abs(val) < 1e-10:
            z_row.append("0")
        else:
            z_row.append(f"{val:.4f}")
    
    # Agregar valor objetivo
    if z_val is not None:
        if abs(z_val) < 1e-10:
            z_row.append("0")
        else:
            z_row.append(f"{z_val:.4f}")
    else:
        z_row.append("-")
    
    table.add_row(*z_row, style="bold magenta")
    
    console.print(table)
    console.print()


def leer_entrada():
    console.print(Panel.fit(
        "[bold cyan]Método Simplex de Dos Fases[/bold cyan]\n"
        "[yellow]Ingresa los datos del problema de programación lineal[/yellow]",
        border_style="bright_blue"
    ))
    
    tipo = input("\n¿El problema es de MAX o MIN? ").strip().upper()
    n = int(input("Número de variables de decisión: "))
    m = int(input("Número de restricciones: "))

    console.print("\n[cyan]Ingrese la función objetivo. Puede usar dos formatos:[/cyan]")
    console.print("  [green]1)[/green] Coeficientes separados por espacio: [yellow]'3 5'[/yellow]")
    console.print("  [green]2)[/green] Forma algebraica: [yellow]'3x1+5x2'[/yellow] o [yellow]'3 x1 + 5 x2'[/yellow]")
    z_input = input("Z = ").strip()
    if 'x' in z_input.lower():
        # parsear forma algebraica
        coefs_dict, max_idx = parse_expression(z_input)
        # Verificar si max_idx excede n
        if max_idx > n:
            console.print(f"[yellow]⚠ Advertencia: La función objetivo tiene variables hasta x{max_idx}, pero declaraste n={n}.[/yellow]")
            console.print(f"[yellow]  Ajustando n a {max_idx}.[/yellow]")
            n = max_idx
        z = [0.0] * n
        for idx, val in coefs_dict.items():
            if idx <= n:
                z[idx - 1] = val
    else:
        z = list(map(float, z_input.split()))
        if len(z) != n:
            console.print(f"[yellow]⚠ Advertencia: Se ingresaron {len(z)} coeficientes pero se esperaban {n}.[/yellow]")
            if len(z) < n:
                console.print(f"[yellow]  Rellenando con ceros hasta {n} coeficientes.[/yellow]")
                z += [0.0] * (n - len(z))
            else:
                console.print(f"[yellow]  Recortando a {n} coeficientes.[/yellow]")
                z = z[:n]

    restricciones = []
    signos = []
    rhs = []

    console.print(f"\n[cyan]Ingrese las restricciones una por una[/cyan]")
    console.print(f"  Ejemplo numérico: [yellow]2 1 <= 6[/yellow]")
    console.print(f"  Ejemplo algebraico: [yellow]4x1 + x2 >= 4[/yellow]")
    console.print(f"  [dim]Si usas coeficientes numéricos, separa por espacios y pon {n} coeficientes.[/dim]")
    
    for i in range(m):
        while True:
            entrada = input(f"Restricción {i+1}: ").strip()
            # intentar parse algebraico si contiene 'x'
            if 'x' in entrada.lower():
                try:
                    coef, signo, b = parse_constraint(entrada, n)
                except Exception as e:
                    console.print(f"[red]✗ Error al parsear la restricción: {e}[/red]")
                    continue
                restricciones.append(coef)
                signos.append(signo)
                rhs.append(b)
                break
            else:
                datos = entrada.split()
                if len(datos) < 3:
                    console.print(f"[red]✗ Entrada inválida. Debes ingresar {n} coeficientes, un signo y un valor RHS.[/red]")
                    continue
                signo = datos[-2]
                try:
                    b = float(datos[-1])
                except ValueError:
                    console.print("[red]✗ El término derecho debe ser un número.[/red]")
                    continue
                try:
                    coef = list(map(float, datos[:-2]))
                except ValueError:
                    console.print("[red]✗ Los coeficientes deben ser números.[/red]")
                    continue
                if len(coef) != n:
                    console.print(f"[red]✗ Número de coeficientes incorrecto: se esperaban {n} y se recibieron {len(coef)}.[/red]")
                    console.print(f"[yellow]  Si una variable no aparece, usa 0 en su posición. Por ejemplo: '0 1 <= 3'[/yellow]")
                    continue
                if signo not in ["<=", ">=", "="]:
                    console.print("[red]✗ Signo inválido. Usa <=, >= o =[/red]")
                    continue
                restricciones.append(coef)
                signos.append(signo)
                rhs.append(b)
                break

    return tipo, z, restricciones, signos, rhs

def construir_basis_inicial(nombres, artificials, A):
    """Construye una base inicial válida para el método simplex.
    Si hay artificiales, la base inicial incluirá ellas.
    Si no, busca columnas identidad (holguras).
    """
    m = A.shape[0]
    basic = []
    used = set()
    
    if artificials:
        # Las artificiales deben estar en la base inicial
        basic = artificials.copy()
        used.update(basic)
    
    # Completar la base con columnas identidad si faltan variables
    for row in range(m):
        if len(basic) == m:
            break
        
        # Verificar si esta fila ya está cubierta por alguna variable básica
        covered = False
        for col in basic:
            if abs(A[row, col]) > 1e-9:
                covered = True
                break
        
        if covered:
            continue
        
        # Buscar una columna identidad para esta fila
        for col in range(A.shape[1]):
            if col in used:
                continue
            colvec = A[:, col]
            # Verificar si es columna identidad (solo un 1 en la posición row)
            if np.count_nonzero(colvec) == 1 and abs(colvec[row] - 1.0) < 1e-9:
                basic.append(col)
                used.add(col)
                break
    
    if len(basic) != m:
        raise RuntimeError(
            f"No se pudo construir una base inicial completa. "
            f"Se encontraron {len(basic)} variables básicas pero se necesitan {m}. "
            f"Revisa las restricciones o la estandarización."
        )
    
    return basic


def parse_expression(expr):
    """Parsea una expresión lineal como '3x1 + 5x2 - x3' y devuelve un dict {index:coef} y el mayor índice encontrado."""
    import re
    expr = expr.replace(' ', '')
    # Asegurar que el primer término tenga signo si es necesario
    if expr and expr[0] not in ['+', '-']:
        expr = '+' + expr
    # encontrar términos con patrón coef? x index
    pattern = re.compile(r'([+-])(\d*\.?\d*)(?:\*?)x(\d+)')
    coefs = {}
    max_idx = 0
    for m in pattern.finditer(expr):
        sign, coef_str, idx = m.groups()
        idx = int(idx)
        max_idx = max(max_idx, idx)
        if coef_str == '':
            coef = 1.0
        else:
            coef = float(coef_str)
        if sign == '-':
            coef = -coef
        coefs[idx] = coefs.get(idx, 0.0) + coef
    return coefs, max_idx


def parse_constraint(text, n_expected=None):
    """Parsea una restricción algebraica como '4x1 + x2 >= 4' y devuelve (coef_list, signo, rhs).
    Si n_expected está dado, devuelve lista de longitud n_expected (rellena con ceros).
    """
    import re
    # separar por los signos >= <= = (buscar en orden de longitud descendente)
    m = re.search(r'(<=|>=|=)', text)
    if not m:
        raise ValueError('No se encontró un signo válido (<=, >=, =)')
    signo = m.group(1)
    parts = text.split(signo, 1)  # Dividir solo en la primera ocurrencia
    if len(parts) < 2:
        raise ValueError('Formato de restricción inválido')
    lhs = parts[0].strip()
    rhs = parts[1].strip()
    # parse RHS número
    try:
        b = float(rhs)
    except ValueError:
        raise ValueError(f'El lado derecho "{rhs}" no es un número válido')
    coefs_dict, max_idx = parse_expression(lhs)
    n = n_expected if n_expected is not None else max_idx
    if n < max_idx:
        n = max_idx
    coef_list = [0.0] * n
    for idx, val in coefs_dict.items():
        if idx <= 0:
            raise ValueError('Los índices de variables deben empezar en 1 (x1, x2, ...).')
        if idx > n:
            # ampliar
            coef_list += [0.0] * (idx - n)
            n = idx
        coef_list[idx - 1] = val
    # si la lista es más larga que n_expected, y n_expected no None, recortar o avisar
    if n_expected is not None and len(coef_list) != n_expected:
        if len(coef_list) < n_expected:
            coef_list += [0.0] * (n_expected - len(coef_list))
        else:
            # recortar
            coef_list = coef_list[:n_expected]
    return coef_list, signo, b


def construir_basis_from_A(A):
    """Construye una base inicial eligiendo columnas linealmente independientes de A de forma codiciosa.
    Devuelve la lista de índices de columnas (en la numeración de A) que forman la base.
    """
    m, total = A.shape
    basic = []
    cur_rank = 0
    for j in range(total):
        if len(basic) == m:
            break
        if not basic:
            candidate = A[:, [j]]
            r = np.linalg.matrix_rank(candidate)
            if r > cur_rank:
                basic.append(j)
                cur_rank = r
        else:
            candidate = A[:, basic + [j]]
            r = np.linalg.matrix_rank(candidate)
            if r > cur_rank:
                basic.append(j)
                cur_rank = r
    if len(basic) != m:
        raise RuntimeError("No se pudo construir una base inicial (columnas independientes insuficientes) en A2.")
    return basic


def simplex_por_b_inv(A, b, c, basic_vars, var_names, maximize=True, show_steps=True):
    """Simplex mediante inversión de B en cada iteración. c corresponde a coeficientes de todas las variables."""
    tol = 1e-9
    m, total = A.shape
    basic = basic_vars.copy()
    it = 0
    max_iterations = 1000  # Prevenir ciclos infinitos
    
    while it < max_iterations:
        it += 1
        B = A[:, basic]
        try:
            B_inv = np.linalg.inv(B)
        except np.linalg.LinAlgError:
            raise RuntimeError("La matriz base es singular.")
        x_B = B_inv @ b
        
        # Verificar factibilidad (valores no negativos)
        if any(x_B < -tol):
            console.print(f"[yellow]⚠ Advertencia: Solución básica con valores negativos en iteración {it}[/yellow]")
            console.print(f"[dim]x_B = {x_B}[/dim]")

        # conjuntos no basicos
        non_basic = [j for j in range(total) if j not in basic]
        N = A[:, non_basic]
        c_B = c[basic]
        c_N = c[non_basic]

        reduced = c_N - c_B @ B_inv @ N
        # objective value
        z_val = c_B @ x_B

        # para imprimir la tabla: reconstruimos B^{-1} * A (todas las columnas)
        b_inv_A = B_inv @ A
        # crear fila de reduced costs en orden de todas variables (reduced_full)
        reduced_full = np.zeros(total)
        for idx, j in enumerate(non_basic):
            reduced_full[j] = reduced[idx]
        # los variables básicas suelen tener reduced cost 0 (por convención)
        # si show_steps, mostrar reduced_full y z_val
        if show_steps:
            console.print(f"\n[bold blue]Iteración {it}[/bold blue]")
            mostrar_tabla_iter(b_inv_A, x_B, reduced_full, var_names, basic, z_val)

        if maximize:
            if all(reduced <= tol):
                return basic, x_B, z_val
            enter_idx = np.argmax(reduced)
            if reduced[enter_idx] <= tol:
                return basic, x_B, z_val
            entering = non_basic[enter_idx]
            d = B_inv @ A[:, entering]
            if all(d <= tol):
                raise RuntimeError("Problema ilimitado.")
            ratios = [x_B[i] / d[i] if d[i] > tol else np.inf for i in range(m)]
            leave_pos = int(np.argmin(ratios))
            basic[leave_pos] = entering
        else:
            # minimize
            if all(reduced >= -tol):
                return basic, x_B, z_val
            enter_idx = int(np.argmin(reduced))
            entering = non_basic[enter_idx]
            if reduced[enter_idx] >= -tol:
                return basic, x_B, z_val
            d = B_inv @ A[:, entering]
            # Si no hay componente positiva en d, es ilimitado (no hay ratio finito)
            if all(d <= tol):
                raise RuntimeError("Problema ilimitado (min).")
            ratios = [x_B[i] / d[i] if d[i] > tol else np.inf for i in range(m)]
            leave_pos = int(np.argmin(ratios))
            basic[leave_pos] = entering
    
    raise RuntimeError(f"El algoritmo no convergió después de {max_iterations} iteraciones. Posible ciclaje.")


def metodo_dos_fases(tipo, z, restricciones, signos, rhs):
    Acoef = np.array(restricciones, dtype=float)
    b = np.array(rhs, dtype=float)
    m, n = Acoef.shape

    # Convertir signos a lista mutable si no lo es
    signos = list(signos)
    
    # Verificar y corregir RHS negativos
    for i in range(m):
        if b[i] < 0:
            console.print(f"[yellow]⚠ Normalizando restricción {i+1}: RHS negativo detectado ({b[i]:.4f})[/yellow]")
            b[i] = -b[i]
            Acoef[i, :] = -Acoef[i, :]
            # Invertir el signo de la restricción
            if signos[i] == "<=":
                signos[i] = ">="
            elif signos[i] == ">=":
                signos[i] = "<="
            # "=" permanece igual
            console.print(f"[green]  ✓ Nueva restricción {i+1}: signo {signos[i]}, RHS {b[i]:.4f}[/green]")

    # Estandarizar
    A = Acoef.copy()
    nombres = [f"X{i+1}" for i in range(n)]
    artificials = []
    # añadir columnas según signos
    for i, s in enumerate(signos):
        if s == "<=":
            col = np.zeros((m, 1)); col[i, 0] = 1
            A = np.hstack((A, col)); nombres.append(f"S{i+1}")
        elif s == ">=":
            col_e = np.zeros((m, 1)); col_e[i, 0] = -1
            A = np.hstack((A, col_e)); nombres.append(f"E{i+1}")
            col_a = np.zeros((m, 1)); col_a[i, 0] = 1
            A = np.hstack((A, col_a)); nombres.append(f"A{i+1}")
            artificials.append(len(nombres) - 1)
        elif s == "=":
            col_a = np.zeros((m, 1)); col_a[i, 0] = 1
            A = np.hstack((A, col_a)); nombres.append(f"A{i+1}")
            artificials.append(len(nombres) - 1)
        else:
            raise ValueError("Signo no reconocido")

    console.print("\n[bold cyan]═══ MATRIZ ESTANDARIZADA ═══[/bold cyan]\n")
    # mostrar la matriz estandarizada (sin asignar todavía una base explícita)
    try:
        # mostrar B^{-1}*A usando identidad (muestra A tal cual) y sin etiquetas de base
        mostrar_tabla_iter(np.eye(m) @ A, b, np.zeros(A.shape[1]), nombres, basic_vars=None, z_val=None)
    except Exception as e:
        # fallback simple si falla Rich
        console.print(f"[yellow]Error al mostrar tabla con Rich: {e}[/yellow]")
        console.print("Matriz A:")
        console.print(A)
        console.print("Vector b:")
        console.print(b)

    # Base inicial
    basic = construir_basis_inicial(nombres, artificials, A)
    
    # Verificar que la base inicial es válida
    B_test = A[:, basic]
    if np.linalg.matrix_rank(B_test) < m:
        raise RuntimeError("La base inicial construida no es linealmente independiente.")
    console.print(f"\n[green]✓ Base inicial construida:[/green] [cyan]{[nombres[i] for i in basic]}[/cyan]")

    # FASE I: minimizar suma de artificiales
    c1 = np.zeros(A.shape[1])
    for idx in artificials:
        c1[idx] = 1.0

    if len(artificials) > 0:
        console.print("\n[bold magenta]═══ FASE I: minimizando suma de variables artificiales ═══[/bold magenta]\n")
        # imprimir la tabla inicial de Fase I con la base encontrada
        try:
            mostrar_tabla_iter(np.eye(m) @ A, b, np.zeros(A.shape[1]), nombres, basic, z_val=None)
        except Exception:
            pass
        basic1, xB1, z1 = simplex_por_b_inv(A, b, c1, basic.copy(), nombres, maximize=False, show_steps=True)
        console.print(f"\n[bold green]✓ Valor óptimo Fase I (suma artificiales) = {z1:.6f}[/bold green]")
        if abs(z1) > 1e-6:
            console.print("[bold red]✗ Problema infactible (Fase I óptimo distinto de 0).[/bold red]")
            return
        # Eliminar columnas artificiales de A y nombres
        keep = [i for i in range(A.shape[1]) if i not in artificials]
        A2 = A[:, keep]
        nombres2 = [nombres[i] for i in keep]
        
        # Mapear la base de Fase I a índices de A2
        # Eliminar artificiales de basic1 y mapear los índices restantes
        basic2 = []
        for var_idx in basic1:
            if var_idx not in artificials:
                # Encontrar el nuevo índice en A2
                new_idx = keep.index(var_idx)
                basic2.append(new_idx)
        
        console.print(f"\n[cyan]Variables básicas después de Fase I (sin artificiales):[/cyan] [yellow]{[nombres2[i] for i in basic2]}[/yellow]")
        
        # Si faltan variables básicas (porque había artificiales en la base),
        # completar con columnas de identidad
        if len(basic2) < m:
            console.print(f"[yellow]⚠ Advertencia: La base óptima de Fase I contenía {m - len(basic2)} variable(s) artificial(es).[/yellow]")
            console.print("[yellow]  Completando la base con columnas de identidad disponibles...[/yellow]")
            used = set(basic2)
            for row in range(m):
                if len(basic2) == m:
                    break
                # Verificar si esta fila ya está cubierta
                covered = False
                for col in basic2:
                    if abs(A2[row, col]) > 1e-9:
                        covered = True
                        break
                if covered:
                    continue
                # Buscar columna de identidad para esta fila
                for col in range(A2.shape[1]):
                    if col in used:
                        continue
                    colvec = A2[:, col]
                    if np.count_nonzero(colvec) == 1 and abs(colvec[row] - 1.0) < 1e-9:
                        basic2.append(col)
                        used.add(col)
                        console.print(f"[green]  ✓ Añadida variable {nombres2[col]} para fila {row + 1}[/green]")
                        break
            
            # Si aún faltan, usar construir_basis_from_A como último recurso
            if len(basic2) < m:
                console.print("[yellow]  No se encontraron suficientes columnas de identidad. Construyendo base de forma codiciosa...[/yellow]")
                basic2 = construir_basis_from_A(A2)
        
        # Verificar que la base para Fase II es válida
        B2_test = A2[:, basic2]
        if np.linalg.matrix_rank(B2_test) < m:
            console.print("[yellow]⚠ Advertencia: La base construida para Fase II no es linealmente independiente.[/yellow]")
            console.print("[yellow]  Reconstruyendo base usando algoritmo codicioso...[/yellow]")
            basic2 = construir_basis_from_A(A2)
        
        console.print(f"\n[green]✓ Base inicial para Fase II:[/green] [cyan]{[nombres2[i] for i in basic2]}[/cyan]")
        console.print(f"[dim]Se eliminaron las columnas artificiales. Columnas restantes: {len(nombres2)}[/dim]")
    else:
        # no hay artificiales
        A2 = A.copy(); nombres2 = nombres.copy(); basic2 = basic.copy()

    # Preparar coeficientes de la función original
    c_orig = np.zeros(A2.shape[1])
    for i in range(len(z)):
        c_orig[i] = z[i]
    # si es MAX convertimos a forma de maximización directamente (nuestro simplex maximiza por defecto)
    maximize = True if tipo == "MAX" else False

    console.print("\n[bold magenta]═══ FASE II: optimizando función objetivo original ═══[/bold magenta]\n")
    basic_final, xB_final, z_final = simplex_por_b_inv(A2, b, c_orig, basic2.copy(), nombres2, maximize=maximize, show_steps=True)
    
    # Mostrar resultado final
    console.print("\n")
    console.print(Panel.fit(
        "[bold green]*** RESULTADO FINAL ***[/bold green]",
        border_style="green"
    ))
    
    # construir vector solución completo
    solution = np.zeros(len(nombres2))
    B = A2[:, basic_final]
    B_inv = np.linalg.inv(B)
    x_B = B_inv @ b
    for i, bi in enumerate(basic_final):
        solution[bi] = x_B[i]
    
    # Crear tabla de resultados
    result_table = Table(
        title="Solución Óptima",
        box=box.DOUBLE_EDGE,
        header_style="bold green"
    )
    result_table.add_column("Variable", style="cyan", justify="center")
    result_table.add_column("Valor", style="yellow", justify="right")
    
    for name, val in zip(nombres2, solution):
        if abs(val) < 1e-10:
            result_table.add_row(name, "0")
        else:
            result_table.add_row(name, f"{val:.6f}")
    
    console.print(result_table)
    
    # Mostrar valor objetivo
    z_text = Text()
    z_text.append("\nZ óptimo = ", style="bold white")
    z_text.append(f"{z_final:.6f}", style="bold green")
    console.print(Panel(z_text, border_style="green", expand=False))


if __name__ == "__main__":
    tipo, z, restricciones, signos, rhs = leer_entrada()
    metodo_dos_fases(tipo, z, restricciones, signos, rhs)
