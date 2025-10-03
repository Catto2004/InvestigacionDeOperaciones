# SimplexSolver.py
# Implementación del método Simplex paso a paso

import numpy as np

class SimplexSolver:
    def __init__(self, c, A, b, modo="Max"):
        """
        c: lista de coeficientes de la función objetivo
        A: matriz de restricciones (listas)
        b: lista de recursos (lado derecho)
        modo: "Max" o "Min"
        """
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.modo = modo
        self.iteraciones = []  # almacena las tablas paso a paso
        self.num_vars = len(c)

        # convertir a problema estándar: añadir variables de holgura
        self.CrearTabla()

    def CrearTabla(self):
        m, n = self.A.shape
        identidad = np.eye(m)
        self.tabla = np.hstack([self.A, identidad, self.b.reshape(-1, 1)])

        # fila objetivo
        z = np.zeros(self.tabla.shape[1])
        z[:self.num_vars] = -self.c if self.modo == "Max" else self.c
        self.tabla = np.vstack([self.tabla, z])

        self.iteraciones.append(self.tabla.copy())

    def Optimo(self):
        fila_obj = self.tabla[-1, :-1]
        if self.modo == "Max":
            return all(c <= 0 for c in fila_obj)
        else:  # Min
            return all(c >= 0 for c in fila_obj)

    def SeleccionarColumna(self):
        fila_obj = self.tabla[-1, :-1]
        return int(np.argmax(fila_obj)) if self.modo == "Min" else int(np.argmax(-fila_obj))

    def SeleccionarFila(self, col_pivote):
        rhs = self.tabla[:-1, -1]
        col = self.tabla[:-1, col_pivote]
        ratios = [rhs[i] / col[i] if col[i] > 0 else np.inf for i in range(len(rhs))]
        return int(np.argmin(ratios))

    def Pivoteo(self, fila_pivote, col_pivote):
        # normalizar fila pivote
        self.tabla[fila_pivote, :] /= self.tabla[fila_pivote, col_pivote]
        # eliminar columna en las demás filas
        for i in range(len(self.tabla)):
            if i != fila_pivote:
                self.tabla[i, :] -= self.tabla[i, col_pivote] * self.tabla[fila_pivote, :]

    def Resolver(self):
        while not self.Optimo():
            col_pivote = self.SeleccionarColumna()
            fila_pivote = self.SeleccionarFila(col_pivote)
            self.Pivoteo(fila_pivote, col_pivote)
            self.iteraciones.append(self.tabla.copy())

        return self.ExtraerSolucion()

    def ExtraerSolucion(self):
        m, n = self.A.shape
        num_vars = self.num_vars
        solucion = np.zeros(num_vars)
        for j in range(num_vars):
            columna = self.tabla[:-1, j]
            if np.count_nonzero(columna) == 1 and 1 in columna:
                fila = np.where(columna == 1)[0][0]
                solucion[j] = self.tabla[fila, -1]

        z = self.tabla[-1, -1] if self.modo == "Max" else -self.tabla[-1, -1]
        return {"x": solucion, "z": z, "iteraciones": self.iteraciones}
