"""
Método de la Esquina Noroeste (Northwest Corner Method)
Para problemas de transporte
"""
import numpy as np


def MetodoEsquinaNoroeste(costos, oferta, demanda):
    """
    Método de la Esquina Noroeste para problemas de transporte.
    
    Args:
        costos: Lista de listas (matriz m x n) con los costos de transporte
        oferta: Lista con la oferta/producción de cada origen
        demanda: Lista con la demanda de cada destino
    
    Returns:
        asignacion: Lista de listas (matriz m x n) con las cantidades asignadas
        costo_total: Costo total de la solución
    """
    # Convertir a numpy arrays para facilitar operaciones
    costos = np.array(costos, dtype=float)
    oferta = np.array(oferta, dtype=float).copy()
    demanda = np.array(demanda, dtype=float).copy()
    
    m, n = costos.shape  # m = orígenes, n = destinos
    asignacion = np.zeros((m, n))
    
    # Validar balance
    if not np.isclose(oferta.sum(), demanda.sum()):
        raise ValueError("La oferta total debe ser igual a la demanda total")
    
    # Comenzar desde la esquina noroeste (0, 0)
    i, j = 0, 0
    
    while i < m and j < n:
        # Asignar el mínimo entre oferta disponible y demanda pendiente
        cantidad = min(oferta[i], demanda[j])
        asignacion[i, j] = cantidad
        
        # Actualizar oferta y demanda
        oferta[i] -= cantidad
        demanda[j] -= cantidad
        
        # Mover a la siguiente celda
        if np.isclose(oferta[i], 0) and np.isclose(demanda[j], 0):
            # Ambos se agotaron, moverse en diagonal
            i += 1
            j += 1
        elif np.isclose(oferta[i], 0):
            # Se agotó la oferta, moverse hacia abajo
            i += 1
        else:
            # Se agotó la demanda, moverse hacia la derecha
            j += 1
    
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
    
    resultado, costo = MetodoEsquinaNoroeste(costos, oferta, demanda)
    
    print("Matriz de asignación:")
    for fila in resultado:
        print([f"{x:.2f}" for x in fila])
    print(f"\nCosto total: {costo:.2f}")
