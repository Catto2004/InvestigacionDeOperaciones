import matplotlib.pyplot as plt
import numpy as np
import random
import os

# ############ Variables ############
# Cabecera
Header = """
\033[1;33m    Investigación de Operaciones:\033[0m\033[33m Metodo Grafico. \033[0m
\033[3m    By Juan Diego Ruiz B. \033[0m
"""
# Arte ASCII
Cat = """\033[93m             ^~^  ,
            ('Y') )
            /   \/
           (\|||/)\033[0m  
"""
# Mensajes de la función de salida.
Menssages = [
    "¡Adios!",    "さようなら!", "Good Bye!",     "Tschüss!", 
    "Au Revoir!", "Увидимся!",  "안녕히 가세요!", "再见!",
    "Ciao!",      "Sometimes goodbye is a second chance!",
    "Auf Wiedersehen!", "Hurrengo arte!", "Feliz Jueves!"
]

global Exit, opt
# Condición de Salida del Menú.
Exit = False
# Opción del Usuario.
opt = 0

# Cofiguración del problema.
Rest = ["x >= 0", "y >= 0"]   # Restricciones del problema.
Conf = "MAX"                  # Valores: 0 -> MIN / 1 -> MAX.
Fobj = "x + y"                # Función Objetivo.
LimX = [0, 9]                 # Limites de los valores de X.
LimY = [0, 9]                 # Limites de los valores de Y.

# Resultados
XOpt = 0                      # Valor Optimo de X.
YOpt = 0                      # Valor Optimo de Y.
Pmed = [[0,0]]                # Puntos de cruce entre las restricciones.

# ############ Funciones ############

# Función de Error
def Error():
    print("\n\033[1;31m    Error: Opción no válida.\a\033[0m")
    input("\033[3m    Presione \033[1mEnter\033[0m\033[3m para continuar...\033[0m")

# Función de Cierre
def Close():
    os.system("cls")
    print("")
    print("\033[1m")
    print(f"           {random.choice(Menssages)}\033[0m")
    print("        -----v------------")
    print(Cat)
    print("\n\n\n\n\n")
    Exit = True
    exit()

# Función para Mostrar las Restricciones
def PrintRestrictions():
    i = 1
    print("\n    Restricciones: ")
    for Restriction in Rest:
        print(f"    {i}. {Restriction}")
        i += 1

# Función para Modificar las Restricciones.
def RestrictionsMenu():
    InterExit = False   # Condición de Salida Interna
    while(InterExit == False):
        os.system("cls")

        # Pantalla principal
        print(Header)
        print(Cat)

        print(f"{Conf} z = {Fobj}")
        PrintRestrictions()

        print("\nEscoge una opción: \n")
        print("    1. Modificar una Restricción.")
        print("    2. Eliminar una Restricción.")
        print("    3. Añadir una Restricción.")
        print("    4. Reiniciar.")

        print("\n    0. Volver.")

        opt = input("\n > ")

        if(opt == 1):           # Modificar una Restricción.
            pass
        elif(opt == 2):         # Eliminar una Restricción.
            pass
        elif(opt == 3):         # Añadir una Restricción.
            pass
        elif(opt == 4):         # Reiniciar las Restricciones.
            pass
        elif(opt == 0):         # Volver al Menú Principal
            Close()
        else:
            Error()

# Función para Encontrar los Puntos de Corte.
def Points():
    pass

# Función para Graficar el problema.
def Grahp():
    pass

# ############ Menú ############
def Menu():
    while(Exit == False):
        os.system("cls")
    
        # Pantalla principal
        print(Header)
        print(Cat)

        print(f"{Conf} z = {Fobj}")
        PrintRestrictions()

        print("\nEscoge una opción: \n")
        print("    1. Modificar Restricciones.")
        print("    2. Modificar Función Objetivo.")
        print("    3. Modificar Objetivo: Min/Max.")
        print("    4. Resolver.")

        print("\n    0. Salir.")

        opt = input("\n > ")

        if(opt == 1):           # Abre menú de Restricciones.
            RestrictionsMenu()
        elif(opt == 2):         # Modifica la Función Objetivo.
            pass
        elif(opt == 3):         # Modifica el objetivo.
            if  (Conf == "MIN"): Conf = "MAX"
            elif(Conf == "MAX"): Conf = "MIN"
        elif(opt == 4):         # Resuelve el problema.
            pass
        elif(opt == 0):         # Salir
            Close()
        else:
            Error()

# ############ Ejecución ############
Menu()