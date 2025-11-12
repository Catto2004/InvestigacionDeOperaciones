"""
Archivo de prueba para los tres métodos de transporte
"""
from EsquinaOeste import metodo_esquina_noroeste
from MenorCosto import metodo_menor_costo
from MetodoVoguel import metodo_vogel


def imprimir_resultado(nombre_metodo, asignacion, costo):
    """Imprime el resultado de forma legible"""
    print(f"\n{'='*60}")
    print(f"{nombre_metodo}")
    print('='*60)
    print("\nMatriz de asignación:")
    for i, fila in enumerate(asignacion):
        print(f"Origen {i+1}: {[f'{x:6.2f}' for x in fila]}")
    print(f"\nCosto total: {costo:.2f}")


# Ejemplo de problema de transporte
# 3 orígenes (fábricas), 4 destinos (almacenes)
costos = [
    [25, 35, 36, 60],
    [55, 30, 45, 38],
    [40, 50, 26, 65],
    [60, 40, 66, 27]
]

oferta = [15, 6, 14, 11]  # Producción de cada fábrica
demanda = [10, 12, 15, 9]  # Demanda de cada almacén

print("="*60)
print("PROBLEMA DE TRANSPORTE")
print("="*60)
print("\nMatriz de Costos:")
for i, fila in enumerate(costos):
    print(f"Origen {i+1}: {fila}")
print(f"\nOferta: {oferta}")
print(f"Demanda: {demanda}")
print(f"Total oferta: {sum(oferta)}")
print(f"Total demanda: {sum(demanda)}")

# Método 1: Esquina Noroeste
resultado1, costo1 = metodo_esquina_noroeste(costos, oferta, demanda)
imprimir_resultado("MÉTODO DE LA ESQUINA NOROESTE", resultado1, costo1)

# Método 2: Menor Costo
resultado2, costo2 = metodo_menor_costo(costos, oferta, demanda)
imprimir_resultado("MÉTODO DEL MENOR COSTO", resultado2, costo2)

# Método 3: Vogel
resultado3, costo3 = metodo_vogel(costos, oferta, demanda)
imprimir_resultado("MÉTODO DE VOGEL (VAM)", resultado3, costo3)

# Comparación
print(f"\n{'='*60}")
print("COMPARACIÓN DE MÉTODOS")
print('='*60)
print(f"Esquina Noroeste: ${costo1:.2f}")
print(f"Menor Costo:      ${costo2:.2f}")
print(f"Vogel (VAM):      ${costo3:.2f}")
print(f"\nMejor solución: ", end="")
mejor_costo = min(costo1, costo2, costo3)
if mejor_costo == costo1:
    print("Esquina Noroeste")
elif mejor_costo == costo2:
    print("Menor Costo")
else:
    print("Vogel (VAM)")
