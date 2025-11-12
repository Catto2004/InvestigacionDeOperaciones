# Método Simplex de Dos Fases con Rich

Este programa implementa el **Método Simplex de Dos Fases** para resolver problemas de programación lineal, con una interfaz mejorada usando la librería **Rich** para mostrar tablas elegantes y coloridas.

## 📦 Instalación

Antes de ejecutar el programa, instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

O instala manualmente:

```bash
pip install numpy rich
```

## 🚀 Uso

Ejecuta el programa:

```bash
python SimplexDosFases.py
```

## 📝 Entrada de Datos

### Función Objetivo
Puedes ingresar la función objetivo en dos formatos:

1. **Coeficientes numéricos**: `3 5`
2. **Forma algebraica**: `3x1 + 5x2` o `3x1+5x2`

### Restricciones
Puedes ingresar restricciones en dos formatos:

1. **Coeficientes numéricos**: `2 1 <= 6`
2. **Forma algebraica**: `4x1 + x2 >= 4`

### Signos de restricción
- `<=` (menor o igual)
- `>=` (mayor o igual)  
- `=` (igual)

## ✨ Características

- ✅ Tablas Simplex con colores y formato elegante usando Rich
- ✅ Soporte para maximización y minimización
- ✅ Manejo automático de RHS negativos
- ✅ Detección de problemas infactibles
- ✅ Detección de problemas ilimitados
- ✅ Validación de bases linealmente independientes
- ✅ Límite de iteraciones para prevenir ciclos infinitos
- ✅ Parsing flexible de entrada (numérica o algebraica)
- ✅ Mensajes informativos con colores

## 📊 Ejemplo

```
¿El problema es de MAX o MIN? MAX
Número de variables de decisión: 2
Número de restricciones: 2

Z = 3x1 + 5x2

Restricción 1: 2x1 + x2 <= 6
Restricción 2: x1 + 2x2 <= 8
```

## 🎨 Salida

El programa mostrará:
- Matriz estandarizada con colores
- Tablas de iteración para Fase I (si hay artificiales)
- Tablas de iteración para Fase II
- Resultado final con tabla elegante y valor objetivo resaltado

## 👨‍💻 Autor

**JDRB** - Investigación de Operaciones
