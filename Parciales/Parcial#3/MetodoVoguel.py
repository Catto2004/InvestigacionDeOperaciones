"""
Método de Aproximación de Vogel (Vogel's Approximation Method - VAM)
Para problemas de transporte
"""
import numpy as np


def MetodoVogel(costos, oferta, demanda):
    """
    Método de Aproximación de Vogel para problemas de transporte.
    Utiliza penalizaciones para seleccionar las mejores asignaciones.
    
    Args:
        costos: Lista de listas (matriz m x n) con los costos de transporte
        oferta: Lista con la oferta/producción de cada origen
        demanda: Lista con la demanda de cada destino
    
    Returns:
        asignacion: Lista de listas (matriz m x n) con las cantidades asignadas
        costo_total: Costo total de la solución
    """
    # Convertir a numpy arrays
    costos = np.array(costos, dtype=float)
    oferta = np.array(oferta, dtype=float).copy()
    demanda = np.array(demanda, dtype=float).copy()
    
    m, n = costos.shape  # m = orígenes, n = destinos
    asignacion = np.zeros((m, n))
    
    # Validar balance
    if not np.isclose(oferta.sum(), demanda.sum()):
        raise ValueError("La oferta total debe ser igual a la demanda total")
    
    # Crear una copia de costos para marcar celdas usadas
    costos_trabajo = costos.copy()
    
    # Listas para rastrear filas y columnas activas
    filas_activas = list(range(m))
    columnas_activas = list(range(n))
    
    while len(filas_activas) > 0 and len(columnas_activas) > 0:
        # Calcular penalizaciones para cada fila activa
        penalizaciones_filas = []
        for i in filas_activas:
            costos_fila = [costos_trabajo[i, j] for j in columnas_activas]
            if len(costos_fila) >= 2:
                costos_ordenados = sorted(costos_fila)
                penalizacion = costos_ordenados[1] - costos_ordenados[0]
            else:
                penalizacion = 0
            penalizaciones_filas.append((penalizacion, i))
        
        # Calcular penalizaciones para cada columna activa
        penalizaciones_columnas = []
        for j in columnas_activas:
            costos_col = [costos_trabajo[i, j] for i in filas_activas]
            if len(costos_col) >= 2:
                costos_ordenados = sorted(costos_col)
                penalizacion = costos_ordenados[1] - costos_ordenados[0]
            else:
                penalizacion = 0
            penalizaciones_columnas.append((penalizacion, j))
        
        # Encontrar la máxima penalización
        max_pen_fila = max(penalizaciones_filas, key=lambda x: x[0]) if penalizaciones_filas else (-1, -1)
        max_pen_col = max(penalizaciones_columnas, key=lambda x: x[0]) if penalizaciones_columnas else (-1, -1)
        
        # Decidir si trabajar con fila o columna
        if max_pen_fila[0] >= max_pen_col[0]:
            # Trabajar con la fila de mayor penalización
            i = max_pen_fila[1]
            # Encontrar el menor costo en esa fila
            costos_fila = [(costos_trabajo[i, j], j) for j in columnas_activas]
            j = min(costos_fila, key=lambda x: x[0])[1]
        else:
            # Trabajar con la columna de mayor penalización
            j = max_pen_col[1]
            # Encontrar el menor costo en esa columna
            costos_col = [(costos_trabajo[i, j], i) for i in filas_activas]
            i = min(costos_col, key=lambda x: x[0])[1]
        
        # Asignar el mínimo entre oferta y demanda
        cantidad = min(oferta[i], demanda[j])
        asignacion[i, j] = cantidad
        
        # Actualizar oferta y demanda
        oferta[i] -= cantidad
        demanda[j] -= cantidad
        
        # Eliminar fila o columna agotada
        if np.isclose(oferta[i], 0):
            filas_activas.remove(i)
        if np.isclose(demanda[j], 0):
            columnas_activas.remove(j)
    
    # Calcular el costo total
    costo_total = np.sum(asignacion * costos)
    
    # Convertir resultado a lista de listas
    asignacion_lista = asignacion.tolist()
    
    return asignacion_lista, float(costo_total)


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo: 3 orígenes, 4 destinos
    costos = [
        [2, 3, 5, 1],
        [4, 1, 3, 2],
        [3, 4, 2, 5]
    ]
    
    oferta = [30, 40, 20]
    demanda = [20, 25, 30, 15]
    
    resultado, costo = MetodoVogel(costos, oferta, demanda)
    
    print("Matriz de asignación:")
    for fila in resultado:
        print([f"{x:.2f}" for x in fila])
    print(f"\nCosto total: {costo:.2f}")
