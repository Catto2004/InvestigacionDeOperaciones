Métodos de Solución para Problemas de Transporte

Implementación de tres métodos heurísticos para encontrar soluciones básicas factibles iniciales en problemas de transporte.

## 📋 Métodos Implementados

### 1. Método de la Esquina Noroeste (Northwest Corner Method)
- **Archivo**: `EsquinaOeste.py`
- **Descripción**: Comienza asignando desde la celda superior izquierda (noroeste) y se mueve hacia la derecha o abajo según se agoten la oferta o demanda.
- **Ventaja**: Simple y rápido
- **Desventaja**: No considera los costos, generalmente da soluciones de costo más alto

### 2. Método del Menor Costo (Least Cost Method)
- **Archivo**: `MenorCosto.py`
- **Descripción**: Asigna primero a las celdas con menor costo de transporte.
- **Ventaja**: Considera los costos, mejores soluciones que Esquina Noroeste
- **Desventaja**: Puede requerir más iteraciones

### 3. Método de Aproximación de Vogel (Vogel's Approximation Method - VAM)
- **Archivo**: `MetodoVoguel.py`
- **Descripción**: Calcula penalizaciones (diferencia entre los dos menores costos) para cada fila y columna, asignando donde la penalización es mayor.
- **Ventaja**: Generalmente da las mejores soluciones iniciales
- **Desventaja**: Más complejo computacionalmente

## 🚀 Uso

### Formato de Entrada

Cada método requiere tres parámetros:

```python
costos = [
    [c11, c12, ..., c1n],  # Costos origen 1 a destinos 1..n
    [c21, c22, ..., c2n],  # Costos origen 2 a destinos 1..n
    ...
    [cm1, cm2, ..., cmn]   # Costos origen m a destinos 1..n
]

oferta = [o1, o2, ..., om]      # Oferta/producción de cada origen
demanda = [d1, d2, ..., dn]     # Demanda de cada destino
```

**Restricción importante**: La suma total de oferta debe ser igual a la suma total de demanda.

### Ejemplo de Uso

```python
from EsquinaOeste import metodo_esquina_noroeste
from MenorCosto import metodo_menor_costo
from MetodoVoguel import metodo_vogel

# Definir el problema
costos = [
    [2, 3, 5, 1],
    [4, 1, 3, 2],
    [3, 4, 2, 5]
]
oferta = [30, 40, 20]
demanda = [20, 25, 30, 15]

# Resolver con cada método
asignacion1, costo1 = metodo_esquina_noroeste(costos, oferta, demanda)
asignacion2, costo2 = metodo_menor_costo(costos, oferta, demanda)
asignacion3, costo3 = metodo_vogel(costos, oferta, demanda)

print(f"Costo Esquina Noroeste: {costo1}")
print(f"Costo Menor Costo: {costo2}")
print(f"Costo Vogel: {costo3}")
```

### Salida

Cada método devuelve:
- **asignacion**: Lista de listas (matriz m×n) con las cantidades asignadas de cada origen a cada destino
- **costo_total**: Valor numérico del costo total de la solución

## 📊 Archivo de Prueba

Ejecuta `test_metodos.py` para comparar los tres métodos con un problema de ejemplo:

```bash
python test_metodos.py
```

## 📦 Requisitos

```bash
pip install numpy
```

## 📝 Notas

- Todos los métodos validan que oferta total = demanda total
- Si no se cumple esta condición, se lanza un `ValueError`
- Las asignaciones cero se representan como 0.0 en la matriz resultado
- Los costos y cantidades pueden ser enteros o flotantes

## 🎯 Comparación de Métodos

En general, para la misma instancia del problema:
- **Vogel** suele dar la mejor solución (menor costo)
- **Menor Costo** da soluciones intermedias
- **Esquina Noroeste** es el más rápido pero con peores costos

Sin embargo, estos son métodos heurísticos para solución inicial. Para obtener la solución óptima, se debe aplicar el **Método de Stepping Stone** o **MODI** sobre cualquiera de estas soluciones iniciales.
