import SolverSimplex

solver = SolverSimplex.SimplexSolver()
solver.initialize("Max", "3x1 + 5x2", [
    "2x1 + 3x2 <= 8",
    "2x1 + x2 >= 4",
    "x1 + x2 <= 5"
])

while True:
    tabla = solver.get_tableau_display_text()
    print(f"\nIteración {solver.iteration} (fase {solver.phase}):")
    print(tabla)
    info = solver.iterate_one()
    if info["status"] != "continue":
        print("STATUS:", info["status"])
        break

print("\nSOLUCIÓN FINAL:")
print(solver.get_solution())
