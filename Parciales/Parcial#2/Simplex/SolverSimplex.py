# SimplexSolver.py
# Implementación del método Simplex paso a paso

import numpy as np

class SimplexSolver:
    def __init__(self, c, A, b, modo="Max"):
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.modo = modo
        self.iteraciones = []           # almacena copias de las tablas
        self.num_vars = len(c)
        self._inicializado = False
        self.tabla = None
        self.CrearTabla()

    # inicializa la tabla y guarda la primera iteración
    def CrearTabla(self):
        m, n = self.A.shape
        identidad = np.eye(m)
        self.tabla = np.hstack([self.A, identidad, self.b.reshape(-1, 1)])
        # fila objetivo (última fila)
        z = np.zeros(self.tabla.shape[1])
        z[:self.num_vars] = -self.c if self.modo == "Max" else self.c
        self.tabla = np.vstack([self.tabla, z])
        self.iteraciones = [self.tabla.copy()]
        self._inicializado = True

    # condición de optimalidad
    def Optimo(self):
        fila_obj = self.tabla[-1, :-1]
        if self.modo == "Max":
            return all(c <= 1e-12 for c in fila_obj)   # tolerancia numérica
        else:
            return all(c >= -1e-12 for c in fila_obj)

    # elegir columna pivote (regla del coste)
    def SeleccionarColumna(self):
        fila_obj = self.tabla[-1, :-1]
        # para MAX queremos el coeficiente más negativo (mayor mejora)
        if self.modo == "Max":
            idx = int(np.argmin(fila_obj))  # más negativo
        else:
            idx = int(np.argmax(fila_obj))  # más positivo para MIN
        return idx

    # elegir fila pivote (mínimo ratio)
    def SeleccionarFila(self, col_pivote):
        rhs = self.tabla[:-1, -1]
        col = self.tabla[:-1, col_pivote]
        ratios = []
        for i in range(len(rhs)):
            aij = col[i]
            if aij > 1e-12:
                ratios.append(rhs[i] / aij)
            else:
                ratios.append(np.inf)
        fila = int(np.argmin(ratios))
        if ratios[fila] == np.inf:
            raise ValueError("Problema no acotado (no hay pivote válido).")
        return fila

    # operación de pivoteo (actualiza la tabla)
    def Pivoteo(self, fila_pivote, col_pivote):
        pivot = self.tabla[fila_pivote, col_pivote]
        if abs(pivot) < 1e-12:
            raise ValueError("Pivote numéricamente nulo.")
        # normalizar fila pivote
        self.tabla[fila_pivote, :] = self.tabla[fila_pivote, :] / pivot
        # eliminar columna en otras filas
        for i in range(self.tabla.shape[0]):
            if i == fila_pivote:
                continue
            factor = self.tabla[i, col_pivote]
            self.tabla[i, :] = self.tabla[i, :] - factor * self.tabla[fila_pivote, :]

    # ejecutar un solo paso (una iteración). devuelve True si se hizo un paso, False si ya era óptimo.
    def Paso(self):
        if not self._inicializado:
            self.CrearTabla()
        if self.Optimo():
            return False
        col = self.SeleccionarColumna()
        fila = self.SeleccionarFila(col)
        self.Pivoteo(fila, col)
        self.iteraciones.append(self.tabla.copy())
        return True

    # resolver todo (ejecuta pasos hasta óptimo o excepción)
    def Resolver(self):
        while not self.Optimo():
            self.paso()
        return self.ExtraerSolucion()

    # extraer solución (x1..xn) y valor z
    def ExtraerSolucion(self):
        m, n = self.A.shape
        solucion = np.zeros(self.num_vars)
        # Para cada variable original j, verificar si columna es básica
        for j in range(self.num_vars):
            columna = self.tabla[:-1, j]
            # columna básica: exactamente un 1 y resto 0 (con tolerancia)
            mask = np.isclose(columna, 0.0, atol=1e-9)
            if np.count_nonzero(~mask) == 1:
                fila = np.where(~mask)[0][0]
                # si el único elemento no es ~1 numéricamente, ignorar
                if abs(self.tabla[fila, j] - 1.0) < 1e-8:
                    solucion[j] = self.tabla[fila, -1]
        z_raw = self.tabla[-1, -1]
        z = z_raw if self.modo == "Max" else -z_raw
        return {"x": solucion, "z": z, "iteraciones": self.iteraciones.copy()}

    # reiniciar (reconstruye la tabla)
    def Reset(self):
        self.iteraciones = []
        self.CrearTabla()