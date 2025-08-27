import tkinter as tk
import pulp

def resolver():
    # Crear el problema de programación lineal entera
    prob = pulp.LpProblem("CuadradoMagico", pulp.LpMinimize)

    # Variables: x[i][j] = número en celda (i,j), 1 <= x <= 9
    x = [[pulp.LpVariable(f"x_{i}_{j}", lowBound=1, upBound=9, cat="Integer")
          for j in range(3)] for i in range(3)]

    # Función objetivo trivial (minimizar 0)
    prob += 0

    # Restricciones de filas
    for i in range(3):
        prob += pulp.lpSum(x[i][j] for j in range(3)) == 15

    # Restricciones de columnas
    for j in range(3):
        prob += pulp.lpSum(x[i][j] for i in range(3)) == 15

    # Restricciones de diagonales
    prob += pulp.lpSum(x[i][i] for i in range(3)) == 15
    prob += pulp.lpSum(x[i][2 - i] for i in range(3)) == 15

    # Restricción: no adyacentes iguales
    direcciones = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    for i in range(3):
        for j in range(3):
            for di,dj in direcciones:
                ni, nj = i+di, j+dj
                if 0 <= ni < 3 and 0 <= nj < 3 and (i < ni or (i == ni and j < nj)):
                    # x[i][j] != x[ni][nj] -> |x[i][j] - x[ni][nj]| >= 1
                    y = pulp.LpVariable(f"bin_{i}_{j}_{ni}_{nj}", cat="Binary")
                    M = 9
                    prob += x[i][j] - x[ni][nj] + M*y >= 1
                    prob += x[ni][nj] - x[i][j] + M*(1-y) >= 1

    # Resolver
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # Mostrar en la interfaz
    for i in range(3):
        for j in range(3):
            valor = int(pulp.value(x[i][j]))
            celdas[i][j].config(text=str(valor))

# ------------------- INTERFAZ TKINTER -------------------

root = tk.Tk()
root.title("Cuadrado Mágico con PL")

celdas = [[None for _ in range(3)] for _ in range(3)]

for i in range(3):
    for j in range(3):
        lbl = tk.Label(root, text="?", width=5, height=2, relief="ridge", font=("Arial",16))
        lbl.grid(row=i, column=j, padx=5, pady=5)
        celdas[i][j] = lbl

btn = tk.Button(root, text="Resolver", command=resolver, font=("Arial",14))
btn.grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()
