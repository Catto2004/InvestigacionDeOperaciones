# Documentación del Sistema de Programación Lineal Interactiva

## 1. Introducción

Este proyecto implementa una **aplicación interactiva en consola** (usando la librería `Textual`) para resolver problemas de **Programación Lineal (PL)** mediante tres métodos fundamentales:

* **Algoritmo Simplex** (primal)
* **Conversión a problema Dual**
* **Algoritmo Dual Simplex**

El objetivo es proporcionar una herramienta visual y educativa para entender el proceso iterativo de estos métodos, mostrando el **tableau paso a paso**, la **función objetivo**, las **restricciones** y la **solución actual**.

El sistema está desarrollado en Python y modularizado en distintas carpetas para mantener una arquitectura clara, flexible y ampliable.

---

## 2. Arquitectura General del Proyecto

El sistema sigue una arquitectura modular basada en componentes, donde cada parte cumple un rol específico:

```plaintext
📦 ProyectoPL/
├── App.py                    # Punto de entrada principal (menú de selección de método)
├── MicroModulos.py           # Widgets reutilizables de la interfaz (restricciones, FO, tabla, solución)
├── Parser.py                 # Analizador de expresiones matemáticas (restricciones y FO)
├── Simplex/
│   ├── Simplex.py            # Pantalla del algoritmo Simplex paso a paso
│   ├── SimplexTCSS.py        # Estilos CSS para la interfaz Simplex
│   └── SolverSimplex.py      # Implementación del solver Simplex (Two-Phase)
├── Dual/
│   ├── Dual.py               # Conversor de problema Primal a Dual (interfaz)
│   └── DualConversor.py      # Lógica de conversión entre formas Primal y Dual
├── DualSimplex/
│   ├── DualSimplex.py        # Pantalla del algoritmo Dual Simplex
│   └── SolverDualSimplex.py  # Implementación del solver Dual Simplex
└── assets/                   # (Opcional) Archivos CSS o recursos adicionales
```

El flujo principal parte del archivo `App.py`, desde donde el usuario elige el método a utilizar.

---

## 3. Descripción de los Módulos

### 3.1 `App.py`

Contiene el **menú principal** de la aplicación. Utiliza `textual.app.App` para renderizar una interfaz interactiva con botones que permiten al usuario elegir entre los tres métodos principales.

**Fragmento destacado:**

```python
class MenuPrincipal(App):
    def compose(self):
        yield Header()
        yield Footer()
        with Vertical(id="menu"):
            yield Static("Seleccione el método a utilizar:", id="tituloMenu")
            yield Button("Algoritmo Simplex", id="botonSimplex")
            yield Button("Conversión Dual", id="botonDual")
            yield Button("Algoritmo Simplex Dual", id="botonAlgDual")
```

Cada botón abre una pantalla distinta (`SimplexApp`, `DualApp`, `DualSimplexApp`).

---

### 3.2 `MicroModulos.py`

Define una serie de **widgets personalizados** que estructuran la interfaz. Estos componentes son reutilizados en todas las pantallas (Simplex, Dual, Dual Simplex):

* `WidgetFuncionObjetivo`: permite ingresar y validar la función objetivo.
* `WidgetRestricciones`: administra las restricciones (agregar, eliminar, validar).
* `WidgetSolucion`: muestra el estado actual de la solución.
* `WidgetTablaIteraciones`: renderiza el tableau Simplex en formato tabular.

**Ejemplo:**

```python
class WidgetFuncionObjetivo(Container):
    def on_input_submitted(self, event: Input.Submitted):
        self.funcion_objetivo = event.value.strip()
        Parser.Parsear(self.funcion_objetivo + "<=0")  # validación sintáctica
```

Estos widgets gestionan la reactividad de la interfaz y notifican al usuario sobre errores o cambios.

---

### 3.3 `Parser.py`

Implementa el **analizador de expresiones** utilizado para interpretar la función objetivo y las restricciones.

* Soporta hasta 10 variables (`x1`, `x2`, ... `x10`).
* Permite expresiones con o sin asterisco (`3x1` o `3*x1`).
* Devuelve un diccionario con coeficientes, operador y constante.

**Salida ejemplo:**

```python
Parsear("3x1 + 2x2 <= 10")
# → {'coef': [3.0, 2.0, 0, ...], 'operador': '<=', 'constante': 10.0}
```

Este módulo es usado por todos los solvers y conversores para estandarizar las entradas del usuario.

---

### 3.4 `Simplex/`

#### a) `Simplex.py`

Pantalla interactiva del **Método Simplex** paso a paso. Permite:

* Ingresar la FO y las restricciones.
* Ejecutar iteraciones manuales.
* Visualizar el tableau actualizado.
* Mostrar mensajes de estado (fase I, fase II, óptimo, ilimitado, infactible).

#### b) `SolverSimplex.py`

Implementa el **algoritmo Simplex paso a paso**, con soporte para **dos fases** (manejo de variables artificiales).

Incluye métodos internos para:

* Inicializar el modelo (`initialize`)
* Calcular soluciones actuales (`_compute_current_solution`)
* Calcular costos reducidos y elegir variables entrantes/salientes
* Ejecutar pivotaciones (`iterate_one`)

**Ejemplo de inicialización:**

```python
solver = SimplexSolver()
solver.initialize("Max", "3x1 + 5x2", ["x1 + 2x2 <= 6", "3x1 + 2x2 <= 12"])
```

El solver devuelve snapshots con el tableau actual y el valor de `Z`, utilizados por `WidgetTablaIteraciones` para la visualización.

#### c) `SimplexTCSS.py`

Define estilos CSS aplicados a los paneles del Simplex (`PanelIzquierdo`, `PanelDerecho`).

---

### 3.5 `Dual/`

#### a) `Dual.py`

Interfaz para la **conversión de un problema Primal a su forma Dual**. Permite ingresar una función objetivo y restricciones, y muestra el problema dual generado.

#### b) `DualConversor.py`

Contiene la lógica matemática de conversión Primal ↔ Dual.

**Flujo general:**

1. Parsea la FO y las restricciones.
2. Calcula la transpuesta de la matriz `A` (intercambiando roles de variables y restricciones).
3. Genera la nueva función objetivo y las condiciones de signo.

**Ejemplo:**

```python
conversor = DualConversor()
resultado = conversor.Convertir("3x1 + 5x2", ["x1 + 2x2 <= 8", "x1 + x2 <= 6"], "Max")
```

Resultado:

```text
Modo: Min
Función Objetivo Dual: Min W = 8*y1 + 6*y2
Restricciones:
  y1 + y2 >= 3
  2*y1 + y2 >= 5
Condiciones:
  y1 >= 0
  y2 >= 0
```

---

### 3.6 `DualSimplex/`

#### a) `DualSimplex.py`

Pantalla interactiva del **Método Dual Simplex**. Combina componentes de entrada (`WidgetFuncionObjetivo`, `WidgetRestricciones`) con un panel para el problema dual convertido y una tabla de iteraciones.

Permite:

* Convertir un problema primal a dual (Ctrl+C)
* Ejecutar iteraciones del Dual Simplex (Ctrl+I)
* Mostrar el tableau y la solución en cada paso.

#### b) `SolverDualSimplex.py`

Implementa el **Algoritmo Dual Simplex**, que mantiene la **optimalidad dual** y busca **factibilidad primal**.

Pasos clave:

1. Selección de variable saliente: la más negativa (infactible)
2. Selección de variable entrante por razón dual mínima
3. Pivotación y actualización del tableau

**Fragmento:**

```python
leaving_row, leaving_var = self._choose_leaving_dual(xB)
entering = self._choose_entering_dual(B_inv, leaving_row, r)
self.basis[leaving_row] = entering
```

---

## 4. Algoritmos Implementados

### 4.1 Simplex (Primal)

* Maximiza o minimiza una FO sujeta a restricciones lineales.
* Maneja desigualdades de tipo `<=`, `>=`, `=` mediante variables de holgura y artificiales.
* Soporta Fase I y II para garantizar factibilidad inicial.

### 4.2 Conversión Dual

* Transforma un problema primal `Max Z = c^T x` en su dual `Min W = b^T y`.
* Intercambia los papeles de restricciones y variables.
* Genera condiciones de signo según el tipo de desigualdad del problema original.

### 4.3 Dual Simplex

* Mantiene optimalidad dual y busca factibilidad primal.
* Ideal para resolver problemas donde el Simplex tradicional falla al iniciar en una solución factible.

---

## 5. Flujo de Ejecución

1. El usuario ejecuta `App.py`.
2. Selecciona el método desde el menú principal.
3. Ingresa la función objetivo y las restricciones.
4. El sistema valida la entrada usando `Parser.py`.
5. El solver correspondiente (`SolverSimplex` o `SolverDualSimplex`) procesa una iteración.
6. El resultado (tableau y valores de variables) se muestra mediante los widgets definidos en `MicroModulos.py`.

---

## 6. Interfaz Gráfica (Textual)

El sistema usa `Textual`, una librería moderna para crear **interfaces TUI** (Text-based User Interfaces). Esto permite presentar la información en paneles, botones y tablas dentro de la terminal.

Cada pantalla hereda de `Screen` y usa `compose()` para definir su estructura visual.

**Ejemplo:**

```python
with Horizontal(id="PanelPrincipal"):
    with Vertical(id="PanelIzquierdo"):
        yield WidgetFuncionObjetivo(id="FuncionObjetivo")
        yield WidgetRestricciones(id="Restricciones")
```

---

## 7. Ejemplo de Uso

**Ejemplo Simplex:**

```
Función objetivo: Max Z = 3x1 + 5x2
Restricciones:
  x1 + 2x2 <= 6
  3x1 + 2x2 <= 12
  x1, x2 >= 0
```

**Pasos:**

1. Ingresar los datos.
2. Presionar Ctrl+I para iterar.
3. Observar el tableau actualizado y el valor de Z.

**Salida esperada:**

```
Z = 24
x1 = 0
x2 = 3
Estado: óptimo
```

---

## 8. Conclusiones

El proyecto ofrece una herramienta completa para el **análisis interactivo de Programación Lineal**, integrando algoritmos clásicos con una interfaz amigable y modular.

El diseño del código permite extenderlo para nuevos métodos (como Big-M o Transporte) sin modificar la estructura central.

---

## 9. Referencias

* Hillier, F. S., & Lieberman, G. J. (2010). *Introduction to Operations Research*.
* Winston, W. L. (2004). *Operations Research: Applications and Algorithms*.
* Documentación oficial de [Textual](https://textual.textualize.io/).
