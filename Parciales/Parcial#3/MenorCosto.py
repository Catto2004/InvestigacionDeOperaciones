"""
Método del Menor Costo (Least Cost Method)
Para problemas de transporte
"""
import numpy as np


def metodo_menor_costo(costos, oferta, demanda):
    """
    Método del Menor Costo para problemas de transporte.
    Asigna primero a las celdas con menor costo.
    
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
    
    # Crear una copia de costos para marcar celdas usadas con infinito
    costos_trabajo = costos.copy()
    
    # Mientras queden ofertas y demandas por satisfacer
    while np.any(oferta > 1e-9) and np.any(demanda > 1e-9):
        # Encontrar la celda con el menor costo no asignado
        min_idx = np.unravel_index(np.argmin(costos_trabajo), costos_trabajo.shape)
        i, j = min_idx
        
        # Asignar el mínimo entre oferta y demanda disponibles
        cantidad = min(oferta[i], demanda[j])
        asignacion[i, j] = cantidad
        
        # Actualizar oferta y demanda
        oferta[i] -= cantidad
        demanda[j] -= cantidad
        
        # Marcar fila o columna como agotada
        if np.isclose(oferta[i], 0):
            # Marcar toda la fila como no disponible
            costos_trabajo[i, :] = np.inf
        if np.isclose(demanda[j], 0):
            # Marcar toda la columna como no disponible
            costos_trabajo[:, j] = np.inf
    
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
    
    resultado, costo = metodo_menor_costo(costos, oferta, demanda)
    
    print("Matriz de asignación:")
    for fila in resultado:
        print([f"{x:.2f}" for x in fila])
    print(f"\nCosto total: {costo:.2f}")
