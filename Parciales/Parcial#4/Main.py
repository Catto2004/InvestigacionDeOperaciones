"""
Algoritmos de Ruta Minima con Interfaz Grafica
Dijkstra | A* | Bellman-Ford
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import heapq
from typing import List, Tuple
import string


class GrafoRutaMinima:
    """Clase que maneja el grafo y los algoritmos de ruta minima."""
    
    def __init__(self):
        self.grafo = nx.DiGraph()
        self.posiciones = {}
        self.heuristicas = {}
    
    def agregar_nodo(self, nombre: str, x: float = None, y: float = None):
        self.grafo.add_node(nombre)
        if x is not None and y is not None:
            self.posiciones[nombre] = (x, y)
    
    def eliminar_nodo(self, nombre: str):
        if nombre in self.grafo:
            self.grafo.remove_node(nombre)
            if nombre in self.posiciones:
                del self.posiciones[nombre]
    
    def agregar_arista(self, origen: str, destino: str, peso: float, bidireccional: bool = False):
        self.grafo.add_edge(origen, destino, weight=peso)
        if bidireccional:
            self.grafo.add_edge(destino, origen, weight=peso)
    
    def eliminar_arista(self, origen: str, destino: str):
        if self.grafo.has_edge(origen, destino):
            self.grafo.remove_edge(origen, destino)
    
    def calcular_heuristicas(self, destino: str):
        if destino not in self.posiciones:
            for nodo in self.grafo.nodes():
                self.heuristicas[nodo] = 0
            return
        
        dx, dy = self.posiciones[destino]
        for nodo in self.grafo.nodes():
            if nodo in self.posiciones:
                nx_pos, ny_pos = self.posiciones[nodo]
                self.heuristicas[nodo] = ((nx_pos - dx)**2 + (ny_pos - dy)**2)**0.5
            else:
                self.heuristicas[nodo] = 0
    
    def dijkstra(self, inicio: str, fin: str) -> Tuple[List[str], float]:
        if inicio not in self.grafo or fin not in self.grafo:
            return [], float('inf')
        
        distancias = {nodo: float('inf') for nodo in self.grafo.nodes()}
        distancias[inicio] = 0
        predecesores = {nodo: None for nodo in self.grafo.nodes()}
        visitados = set()
        cola = [(0, inicio)]
        
        while cola:
            dist_actual, nodo_actual = heapq.heappop(cola)
            
            if nodo_actual in visitados:
                continue
            
            visitados.add(nodo_actual)
            
            if nodo_actual == fin:
                break
            
            for vecino in self.grafo.neighbors(nodo_actual):
                if vecino not in visitados:
                    peso = self.grafo[nodo_actual][vecino]['weight']
                    nueva_dist = dist_actual + peso
                    
                    if nueva_dist < distancias[vecino]:
                        distancias[vecino] = nueva_dist
                        predecesores[vecino] = nodo_actual
                        heapq.heappush(cola, (nueva_dist, vecino))
        
        camino = []
        nodo = fin
        while nodo is not None:
            camino.append(nodo)
            nodo = predecesores[nodo]
        camino.reverse()
        
        if not camino or camino[0] != inicio:
            return [], float('inf')
        
        return camino, distancias[fin]
    
    def a_estrella(self, inicio: str, fin: str) -> Tuple[List[str], float]:
        if inicio not in self.grafo or fin not in self.grafo:
            return [], float('inf')
        
        self.calcular_heuristicas(fin)
        
        g_score = {nodo: float('inf') for nodo in self.grafo.nodes()}
        g_score[inicio] = 0
        f_score = {nodo: float('inf') for nodo in self.grafo.nodes()}
        f_score[inicio] = self.heuristicas[inicio]
        
        predecesores = {nodo: None for nodo in self.grafo.nodes()}
        abiertos = [(f_score[inicio], inicio)]
        cerrados = set()
        
        while abiertos:
            _, nodo_actual = heapq.heappop(abiertos)
            
            if nodo_actual in cerrados:
                continue
            
            if nodo_actual == fin:
                break
            
            cerrados.add(nodo_actual)
            
            for vecino in self.grafo.neighbors(nodo_actual):
                if vecino in cerrados:
                    continue
                
                peso = self.grafo[nodo_actual][vecino]['weight']
                tentativo_g = g_score[nodo_actual] + peso
                
                if tentativo_g < g_score[vecino]:
                    predecesores[vecino] = nodo_actual
                    g_score[vecino] = tentativo_g
                    f_score[vecino] = tentativo_g + self.heuristicas[vecino]
                    heapq.heappush(abiertos, (f_score[vecino], vecino))
        
        camino = []
        nodo = fin
        while nodo is not None:
            camino.append(nodo)
            nodo = predecesores[nodo]
        camino.reverse()
        
        if not camino or camino[0] != inicio:
            return [], float('inf')
        
        return camino, g_score[fin]
    
    def bellman_ford(self, inicio: str, fin: str) -> Tuple[List[str], float]:
        if inicio not in self.grafo or fin not in self.grafo:
            return [], float('inf')
        
        nodos = list(self.grafo.nodes())
        distancias = {nodo: float('inf') for nodo in nodos}
        distancias[inicio] = 0
        predecesores = {nodo: None for nodo in nodos}
        
        for _ in range(len(nodos) - 1):
            for u, v, data in self.grafo.edges(data=True):
                peso = data['weight']
                if distancias[u] + peso < distancias[v]:
                    distancias[v] = distancias[u] + peso
                    predecesores[v] = u
        
        for u, v, data in self.grafo.edges(data=True):
            if distancias[u] + data['weight'] < distancias[v]:
                return [], float('-inf')
        
        camino = []
        nodo = fin
        while nodo is not None:
            camino.append(nodo)
            nodo = predecesores[nodo]
        camino.reverse()
        
        if not camino or camino[0] != inicio:
            return [], float('inf')
        
        return camino, distancias[fin]
    
    def limpiar(self):
        self.grafo.clear()
        self.posiciones.clear()
        self.heuristicas.clear()


class AplicacionRutaMinima:
    """Interfaz grafica principal."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Algoritmos de Ruta Minima - Dijkstra | A* | Bellman-Ford")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.grafo = GrafoRutaMinima()
        self.camino_actual = []
        
        # Variables para interaccion con mouse
        self.modo_interaccion = tk.StringVar(value="agregar_nodo")
        self.nodo_seleccionado = None
        self.contador_nodos = 0
        
        self.crear_interfaz()
        self.actualizar_grafo()
        self.conectar_eventos_mouse()
    
    def crear_interfaz(self):
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.panel_izquierdo = ttk.Frame(self.main_frame, width=350)
        self.panel_izquierdo.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.panel_izquierdo.pack_propagate(False)
        
        self.panel_derecho = ttk.Frame(self.main_frame)
        self.panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.crear_panel_nodos()
        self.crear_panel_algoritmos()
        self.crear_panel_resultados()
        self.crear_panel_grafo()
    
    def crear_panel_nodos(self):
        frame = ttk.LabelFrame(self.panel_izquierdo, text=" Modo de Interaccion", padding="10")
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Seleccione modo (clic en grafo):").pack(anchor=tk.W)
        
        ttk.Radiobutton(frame, text="Agregar Nodo (clic izq.)", 
                       variable=self.modo_interaccion, value="agregar_nodo").pack(anchor=tk.W)
        ttk.Radiobutton(frame, text="Conectar Nodos (clic en 2 nodos)", 
                       variable=self.modo_interaccion, value="conectar").pack(anchor=tk.W)
        ttk.Radiobutton(frame, text="Eliminar Nodo (clic en nodo)", 
                       variable=self.modo_interaccion, value="eliminar_nodo").pack(anchor=tk.W)
        ttk.Radiobutton(frame, text="Mover Nodo (arrastrar)", 
                       variable=self.modo_interaccion, value="mover").pack(anchor=tk.W)
        
        # Estado de seleccion
        self.label_seleccion = ttk.Label(frame, text="", foreground="blue")
        self.label_seleccion.pack(anchor=tk.W, pady=5)
        
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Opciones de conexion
        self.var_bidireccional = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Conexiones Bidireccionales", 
                       variable=self.var_bidireccional).pack(anchor=tk.W)
        
        peso_frame = ttk.Frame(frame)
        peso_frame.pack(fill=tk.X, pady=5)
        ttk.Label(peso_frame, text="Peso por defecto:").pack(side=tk.LEFT)
        self.entry_peso = ttk.Entry(peso_frame, width=8)
        self.entry_peso.pack(side=tk.LEFT, padx=5)
        self.entry_peso.insert(0, "1")
        
        ttk.Button(frame, text="Cancelar Seleccion", 
                  command=self.cancelar_seleccion).pack(fill=tk.X, pady=5)
    
    def crear_panel_algoritmos(self):
        frame = ttk.LabelFrame(self.panel_izquierdo, text=" Resolver Ruta Minima", padding="10")
        frame.pack(fill=tk.X, pady=5)
        
        nodos_frame = ttk.Frame(frame)
        nodos_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(nodos_frame, text="Inicio:").pack(side=tk.LEFT)
        self.combo_inicio = ttk.Combobox(nodos_frame, width=8, state="readonly")
        self.combo_inicio.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(nodos_frame, text="Fin:").pack(side=tk.LEFT, padx=(10, 0))
        self.combo_fin = ttk.Combobox(nodos_frame, width=8, state="readonly")
        self.combo_fin.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame, text="Seleccione el algoritmo:").pack(anchor=tk.W, pady=(10, 5))
        
        btn_style = {'width': 25}
        ttk.Button(frame, text="Dijkstra", command=lambda: self.resolver("dijkstra"), **btn_style).pack(pady=2)
        ttk.Button(frame, text="A* (A-Estrella)", command=lambda: self.resolver("a_estrella"), **btn_style).pack(pady=2)
        ttk.Button(frame, text="Bellman-Ford", command=lambda: self.resolver("bellman_ford"), **btn_style).pack(pady=2)
        
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        ttk.Button(frame, text="Comparar Todos", command=self.comparar_todos, **btn_style).pack(pady=2)
    
    def crear_panel_resultados(self):
        frame = ttk.LabelFrame(self.panel_izquierdo, text=" Resultados", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Botones arriba para que sean visibles
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_grafo).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Ejemplo", command=self.cargar_ejemplo).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Colombia", command=self.cargar_ejemplo_colombia).pack(side=tk.LEFT, padx=2)
        
        self.text_resultados = tk.Text(frame, height=10, width=40, font=('Consolas', 10))
        self.text_resultados.pack(fill=tk.BOTH, expand=True)
    
    def crear_panel_grafo(self):
        frame = ttk.LabelFrame(self.panel_derecho, text=" Visualizacion del Grafo (Haz clic para interactuar)", padding="5")
        frame.pack(fill=tk.BOTH, expand=True)
        
        self.figura = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figura.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.figura, master=frame)
        self.canvas.draw()
        
        # Barra de herramientas de navegación (zoom, pan, guardar, etc.)
        toolbar_frame = ttk.Frame(frame)
        toolbar_frame.pack(fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Instrucciones
        instrucciones = ttk.Label(frame, text="Clic izq: accion segun modo | Clic der: cancelar | Arrastrar: mover nodo (en modo mover)")
        instrucciones.pack(fill=tk.X)
    
    def conectar_eventos_mouse(self):
        """Conecta los eventos del mouse al canvas."""
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.nodo_arrastrando = None
    
    def actualizar_combos(self):
        nodos = list(self.grafo.grafo.nodes())
        for combo in [self.combo_inicio, self.combo_fin]:
            combo['values'] = nodos
    
    def actualizar_grafo(self):
        self.ax.clear()
        
        if len(self.grafo.grafo.nodes()) == 0:
            self.ax.text(0.5, 0.5, 'Grafo vacio\n\nAgregue nodos para comenzar', 
                        ha='center', va='center', fontsize=14, color='gray',
                        transform=self.ax.transAxes)
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
        else:
            if not self.grafo.posiciones or len(self.grafo.posiciones) < len(self.grafo.grafo.nodes()):
                self.grafo.posiciones = nx.spring_layout(self.grafo.grafo, seed=42)
            
            colores_nodos = []
            for nodo in self.grafo.grafo.nodes():
                if self.nodo_seleccionado and nodo == self.nodo_seleccionado:
                    colores_nodos.append('#FF00FF')  # Magenta - Seleccionado
                elif self.camino_actual and nodo == self.camino_actual[0]:
                    colores_nodos.append('#00FF00')  # Verde - Inicio
                elif self.camino_actual and nodo == self.camino_actual[-1]:
                    colores_nodos.append('#FF4444')  # Rojo - Fin
                elif self.camino_actual and nodo in self.camino_actual:
                    colores_nodos.append('#FFFF00')  # Amarillo - En camino
                else:
                    colores_nodos.append('#87CEEB')  # Azul claro - Normal
            
            nx.draw_networkx_nodes(self.grafo.grafo, self.grafo.posiciones, ax=self.ax,
                                  node_color=colores_nodos, node_size=500,
                                  edgecolors='black', linewidths=1.5)
            
            nx.draw_networkx_labels(self.grafo.grafo, self.grafo.posiciones, ax=self.ax,
                                   font_size=8, font_weight='normal')
            
            aristas_camino = []
            aristas_normales = []
            
            if self.camino_actual:
                for i in range(len(self.camino_actual) - 1):
                    aristas_camino.append((self.camino_actual[i], self.camino_actual[i + 1]))
            
            for arista in self.grafo.grafo.edges():
                if arista not in aristas_camino:
                    aristas_normales.append(arista)
            
            nx.draw_networkx_edges(self.grafo.grafo, self.grafo.posiciones, ax=self.ax,
                                  edgelist=aristas_normales, edge_color='gray',
                                  arrows=True, arrowsize=20,
                                  connectionstyle="arc3,rad=0.1")
            
            if aristas_camino:
                nx.draw_networkx_edges(self.grafo.grafo, self.grafo.posiciones, ax=self.ax,
                                      edgelist=aristas_camino, edge_color='#FF4500',
                                      width=3, arrows=True, arrowsize=25,
                                      connectionstyle="arc3,rad=0.1")
            
            etiquetas = nx.get_edge_attributes(self.grafo.grafo, 'weight')
            nx.draw_networkx_edge_labels(self.grafo.grafo, self.grafo.posiciones, ax=self.ax,
                                        edge_labels=etiquetas, font_size=10,
                                        font_color='darkred')
        
        self.ax.set_title("Grafo de Rutas", fontsize=14, fontweight='bold')
        self.ax.axis('off')
        self.ax.set_xlim(-0.10, 1.18)
        self.ax.set_ylim(-0.40, 1.70)
        self.figura.tight_layout()
        self.canvas.draw()
        
        self.actualizar_combos()
    
    def obtener_nodo_en_posicion(self, x, y, tolerancia=0.05):
        """Encuentra si hay un nodo cerca de la posicion dada."""
        for nodo, pos in self.grafo.posiciones.items():
            dist = ((pos[0] - x)**2 + (pos[1] - y)**2)**0.5
            if dist < tolerancia:
                return nodo
        return None
    
    def generar_nombre_nodo(self):
        """Genera un nombre automatico para el nodo."""
        letras = string.ascii_uppercase
        while True:
            if self.contador_nodos < 26:
                nombre = letras[self.contador_nodos]
            else:
                nombre = letras[self.contador_nodos // 26 - 1] + letras[self.contador_nodos % 26]
            self.contador_nodos += 1
            if nombre not in self.grafo.grafo.nodes():
                return nombre
    
    def on_click(self, event):
        """Maneja el evento de clic del mouse."""
        if event.inaxes != self.ax:
            return
        
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
        
        # Clic derecho cancela seleccion
        if event.button == 3:
            self.cancelar_seleccion()
            return
        
        modo = self.modo_interaccion.get()
        nodo_clickeado = self.obtener_nodo_en_posicion(x, y)
        
        if modo == "agregar_nodo":
            if nodo_clickeado is None:
                nombre = self.generar_nombre_nodo()
                self.grafo.agregar_nodo(nombre, x, y)
                self.mostrar_mensaje(f"Nodo '{nombre}' agregado en ({x:.2f}, {y:.2f})")
                self.actualizar_grafo()
            else:
                self.mostrar_mensaje(f"Ya existe el nodo '{nodo_clickeado}' ahi")
        
        elif modo == "conectar":
            if nodo_clickeado:
                if self.nodo_seleccionado is None:
                    self.nodo_seleccionado = nodo_clickeado
                    self.label_seleccion.config(text=f"Origen: {nodo_clickeado} -> Seleccione destino")
                    self.mostrar_mensaje(f"Nodo '{nodo_clickeado}' seleccionado como origen.\nHaz clic en el nodo destino.")
                else:
                    if nodo_clickeado != self.nodo_seleccionado:
                        # Pedir peso
                        try:
                            peso = float(self.entry_peso.get())
                        except:
                            peso = 1.0
                        
                        # Preguntar peso con dialogo
                        peso_str = simpledialog.askstring("Peso del camino", 
                                                         f"Peso de {self.nodo_seleccionado} -> {nodo_clickeado}:",
                                                         initialvalue=str(peso))
                        if peso_str:
                            try:
                                peso = float(peso_str)
                            except:
                                peso = 1.0
                            
                            bidireccional = self.var_bidireccional.get()
                            self.grafo.agregar_arista(self.nodo_seleccionado, nodo_clickeado, peso, bidireccional)
                            
                            direccion = "<->" if bidireccional else "->"
                            self.mostrar_mensaje(f"Camino creado: {self.nodo_seleccionado} {direccion} {nodo_clickeado}\nPeso: {peso}")
                    
                    self.cancelar_seleccion()
                    self.actualizar_grafo()
            else:
                self.mostrar_mensaje("Haz clic en un nodo existente")
        
        elif modo == "eliminar_nodo":
            if nodo_clickeado:
                self.grafo.eliminar_nodo(nodo_clickeado)
                self.camino_actual = []
                self.mostrar_mensaje(f"Nodo '{nodo_clickeado}' eliminado")
                self.actualizar_grafo()
            else:
                self.mostrar_mensaje("Haz clic en un nodo para eliminarlo")
        
        elif modo == "mover":
            if nodo_clickeado:
                self.nodo_arrastrando = nodo_clickeado
                self.label_seleccion.config(text=f"Moviendo: {nodo_clickeado}")
    
    def on_motion(self, event):
        """Maneja el movimiento del mouse (para arrastrar nodos)."""
        if self.nodo_arrastrando and event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            if x is not None and y is not None:
                self.grafo.posiciones[self.nodo_arrastrando] = (x, y)
                self.actualizar_grafo()
    
    def on_release(self, event):
        """Maneja cuando se suelta el boton del mouse."""
        if self.nodo_arrastrando:
            self.mostrar_mensaje(f"Nodo '{self.nodo_arrastrando}' movido")
            self.nodo_arrastrando = None
            self.label_seleccion.config(text="")
    
    def cancelar_seleccion(self):
        """Cancela la seleccion actual."""
        self.nodo_seleccionado = None
        self.nodo_arrastrando = None
        self.label_seleccion.config(text="")
        self.actualizar_grafo()
    
    def resolver(self, algoritmo: str):
        inicio = self.combo_inicio.get()
        fin = self.combo_fin.get()
        
        if not inicio or not fin:
            messagebox.showwarning("Advertencia", "Seleccione nodo de inicio y fin")
            return
        
        if inicio == fin:
            messagebox.showwarning("Advertencia", "Inicio y fin deben ser diferentes")
            return
        
        if algoritmo == "dijkstra":
            camino, distancia = self.grafo.dijkstra(inicio, fin)
            nombre_algo = "DIJKSTRA"
        elif algoritmo == "a_estrella":
            camino, distancia = self.grafo.a_estrella(inicio, fin)
            nombre_algo = "A* (A-ESTRELLA)"
        else:
            camino, distancia = self.grafo.bellman_ford(inicio, fin)
            nombre_algo = "Distancia Minima"
        
        self.camino_actual = camino
        
        resultado = f"{'='*35}\n"
        resultado += f"  {nombre_algo}\n"
        resultado += f"{'='*35}\n\n"
        
        if camino and distancia != float('inf'):
            resultado += f"Camino: {' -> '.join(camino)}\n\n"
            resultado += f"Distancia total: {distancia:.2f}\n"
        elif distancia == float('-inf'):
            resultado += "Se detecto un ciclo negativo\n"
        else:
            resultado += "No se encontro un camino\n"
        
        self.mostrar_mensaje(resultado)
        self.actualizar_grafo()
    
    def comparar_todos(self):
        inicio = self.combo_inicio.get()
        fin = self.combo_fin.get()
        
        if not inicio or not fin:
            messagebox.showwarning("Advertencia", "Seleccione nodo de inicio y fin")
            return
        
        resultado = "="*35 + "\n"
        resultado += "  COMPARACION DE ALGORITMOS\n"
        resultado += "="*35 + "\n\n"
        
        camino1, dist1 = self.grafo.dijkstra(inicio, fin)
        resultado += "DIJKSTRA:\n"
        if camino1:
            resultado += f"  Camino: {' -> '.join(camino1)}\n"
            resultado += f"  Distancia: {dist1:.2f}\n\n"
        else:
            resultado += "  No encontro camino\n\n"
        
        camino2, dist2 = self.grafo.a_estrella(inicio, fin)
        resultado += "A* (A-ESTRELLA):\n"
        if camino2:
            resultado += f"  Camino: {' -> '.join(camino2)}\n"
            resultado += f"  Distancia: {dist2:.2f}\n\n"
        else:
            resultado += "  No encontro camino\n\n"
        
        camino3, dist3 = self.grafo.bellman_ford(inicio, fin)
        resultado += "BELLMAN-FORD:\n"
        if camino3:
            resultado += f"  Camino: {' -> '.join(camino3)}\n"
            resultado += f"  Distancia: {dist3:.2f}\n"
        else:
            resultado += "  No encontro camino\n"
        
        self.camino_actual = camino1 if camino1 else camino2 if camino2 else camino3
        
        self.mostrar_mensaje(resultado)
        self.actualizar_grafo()
    
    def limpiar_grafo(self):
        if messagebox.askyesno("Confirmar", "Desea eliminar todo el grafo?"):
            self.grafo.limpiar()
            self.camino_actual = []
            self.contador_nodos = 0
            self.cancelar_seleccion()
            self.mostrar_mensaje("Grafo limpiado")
            self.actualizar_grafo()
    
    def cargar_ejemplo(self):
        self.grafo.limpiar()
        self.contador_nodos = 6  # Ya hay A-F
        
        # Normalizar posiciones a rango 0-1
        nodos = [
            ('A', 0.1, 0.5), ('B', 0.3, 0.8), ('C', 0.3, 0.2),
            ('D', 0.6, 0.8), ('E', 0.6, 0.2), ('F', 0.9, 0.5)
        ]
        
        for nombre, x, y in nodos:
            self.grafo.agregar_nodo(nombre, x, y)
        
        aristas = [
            ('A', 'B', 4), ('A', 'C', 2), ('B', 'D', 3),
            ('B', 'E', 1), ('C', 'B', 1), ('C', 'E', 5),
            ('D', 'F', 2), ('E', 'D', 1), ('E', 'F', 4)
        ]
        
        for origen, destino, peso in aristas:
            self.grafo.agregar_arista(origen, destino, peso)
        
        self.camino_actual = []
        self.cancelar_seleccion()
        self.mostrar_mensaje("Ejemplo cargado\n\nNodos: A, B, C, D, E, F\n\nModos de interaccion:\n- Agregar Nodo: clic en area vacia\n- Conectar: clic en 2 nodos\n- Mover: arrastrar nodo")
        self.actualizar_grafo()
    
    def cargar_ejemplo_colombia(self):
        """Carga el mapa de Colombia con ciudades principales y municipios intermedios."""
        self.grafo.limpiar()
        
        # Coordenadas normalizadas (0-1) basadas en posición geográfica aproximada
        # Colombia: Lat 12°N a -4°S, Lon -79°W a -67°W
        # Transformamos: x = (lon + 79) / 12, y = (lat + 4) / 16
        
        ciudades = [
            # Capitales y ciudades principales (espaciado vertical x1.3)
            ("Bogotá", 0.55, 0.65),           # Cundinamarca
            ("Medellín", 0.30, 0.94),         # Antioquia  
            ("Cali", 0.20, 0.29),             # Valle del Cauca
            ("Barranquilla", 0.50, 1.53),     # Atlántico
            ("Cartagena", 0.30, 1.46),        # Bolívar
            ("Cúcuta", 0.95, 1.07),           # Norte de Santander
            ("Bucaramanga", 0.78, 0.94),      # Santander
            ("Pereira", 0.28, 0.68),          # Risaralda
            ("Manizales", 0.32, 0.81),        # Caldas
            ("Santa Marta", 0.58, 1.59),      # Magdalena
            ("Ibagué", 0.45, 0.55),           # Tolima
            ("Pasto", 0.12, -0.20),           # Nariño
            ("Neiva", 0.52, 0.23),            # Huila
            ("Villavicencio", 0.78, 0.49),    # Meta
            ("Armenia", 0.22, 0.59),          # Quindío
            ("Popayán", 0.18, 0.03),          # Cauca
            ("Montería", 0.15, 1.24),         # Córdoba
            ("Valledupar", 0.68, 1.33),       # Cesar
            ("Tunja", 0.62, 0.75),            # Boyacá
            ("Florencia", 0.50, -0.10),       # Caquetá
            
            # Municipios intermedios importantes
            ("Honda", 0.48, 0.78),            # Tolima - conexión histórica
            ("Girardot", 0.52, 0.55),         # Cundinamarca
            ("La Dorada", 0.42, 0.88),        # Caldas
            ("Barrancabermeja", 0.60, 1.14),  # Santander - río Magdalena
            ("Sogamoso", 0.78, 0.75),         # Boyacá
            ("Duitama", 0.72, 0.81),          # Boyacá
            ("Aguachica", 0.68, 1.24),        # Cesar
            ("Ocaña", 0.85, 1.14),            # Norte de Santander
            ("Buga", 0.12, 0.42),             # Valle del Cauca
            ("Palmira", 0.15, 0.34),          # Valle del Cauca
            ("Tulúa", 0.08, 0.49),            # Valle del Cauca
            ("Cartago", 0.18, 0.62),          # Valle del Cauca
            ("Ipiales", 0.08, -0.29),         # Nariño - frontera Ecuador
            ("Tumaco", 0.02, -0.10),          # Nariño - costa pacífica
            ("Buenaventura", 0.02, 0.29),     # Valle - puerto pacífico
            ("Sincelejo", 0.35, 1.30),        # Sucre
            ("Magangué", 0.42, 1.27),         # Bolívar
            ("Caucasia", 0.32, 1.11),         # Antioquia
            ("Apartadó", 0.08, 1.11),         # Antioquia - Urabá
            ("Riohacha", 0.75, 1.59),         # La Guajira
            ("Pitalito", 0.35, 0.07),         # Huila - entre Neiva y Popayán
            
            # Oriente colombiano (Llanos y Amazonía)
            ("San Vicente del Caguán", 0.62, -0.03), # Caquetá
            ("San José del Guaviare", 0.72, 0.16),   # Guaviare
            ("Yopal", 0.82, 0.68),            # Casanare
            ("Arauca", 0.95, 0.94),           # Arauca
            ("Puerto Carreño", 1.05, 0.72),   # Vichada
        ]
        
        # Carreteras principales con distancias aproximadas en km
        carreteras = [
            # Ruta Caribe
            ("Bogotá", "Tunja", 123),
            ("Tunja", "Duitama", 50),
            ("Duitama", "Sogamoso", 20),
            ("Tunja", "Bucaramanga", 287),
            ("Bucaramanga", "Cúcuta", 192),
            ("Bucaramanga", "Barrancabermeja", 115),
            ("Barrancabermeja", "Aguachica", 145),
            ("Aguachica", "Valledupar", 165),
            ("Valledupar", "Santa Marta", 166),
            ("Santa Marta", "Barranquilla", 100),
            ("Barranquilla", "Cartagena", 120),
            ("Valledupar", "Riohacha", 173),
            
            # Ruta Central
            ("Bogotá", "Girardot", 134),
            ("Girardot", "Ibagué", 104),
            ("Ibagué", "Armenia", 82),
            ("Armenia", "Pereira", 45),
            ("Pereira", "Manizales", 53),
            ("Manizales", "Medellín", 194),
            ("Ibagué", "Honda", 100),
            ("Honda", "La Dorada", 35),
            ("La Dorada", "Medellín", 180),
            
            # Ruta Occidente  
            ("Armenia", "Cartago", 65),
            ("Cartago", "Pereira", 50),
            ("Cartago", "Tulúa", 102),
            ("Tulúa", "Buga", 32),
            ("Buga", "Palmira", 48),
            ("Palmira", "Cali", 25),
            ("Cali", "Buenaventura", 141),
            ("Cali", "Popayán", 140),
            ("Popayán", "Pasto", 258),
            ("Pasto", "Ipiales", 80),
            ("Pasto", "Tumaco", 300),
            
            # Ruta Huila-Caquetá
            ("Bogotá", "Neiva", 312),
            ("Ibagué", "Neiva", 210),
            ("Neiva", "Pitalito", 188),
            ("Pitalito", "Popayán", 180),
            ("Neiva", "Florencia", 262),
            ("Florencia", "San Vicente del Caguán", 153),
            
            # Ruta Llanos y Oriente
            ("Bogotá", "Villavicencio", 120),
            ("Villavicencio", "San José del Guaviare", 277),
            ("Bogotá", "Yopal", 387),
            ("Yopal", "Arauca", 285),
            ("Villavicencio", "Puerto Carreño", 858),
            ("Yopal", "Sogamoso", 215),
            
            # Costa Caribe
            ("Cartagena", "Sincelejo", 195),
            ("Sincelejo", "Montería", 95),
            ("Sincelejo", "Magangué", 95),
            ("Magangué", "Cartagena", 200),
            
            # Conexión Antioquia
            ("Medellín", "Caucasia", 280),
            ("Caucasia", "Montería", 135),
            ("Montería", "Apartadó", 250),
            ("Medellín", "Apartadó", 344),
            
            # Otras conexiones importantes
            ("Cúcuta", "Ocaña", 195),
            ("Ocaña", "Aguachica", 115),
            ("Bogotá", "Honda", 145),
        ]
        
        # Agregar ciudades como nodos
        for nombre, x, y in ciudades:
            self.grafo.agregar_nodo(nombre, x, y)
        
        # Agregar carreteras bidireccionales
        for origen, destino, distancia in carreteras:
            self.grafo.agregar_arista(origen, destino, distancia, bidireccional=True)
        
        self.contador_nodos = len(ciudades)
        self.camino_actual = []
        self.cancelar_seleccion()
        
        mensaje = """🇨🇴 Mapa de Colombia Cargado

Ciudades: {} nodos
Carreteras: {} conexiones

Incluye:
• Capitales departamentales
• Ciudades intermedias importantes
• Distancias reales aproximadas (km)

Ejemplos de rutas:
• Bogotá → Cartagena (via Bucaramanga)
• Cali → Medellín (via Pereira)
• Bogotá → Santa Marta

Selecciona origen y destino para
calcular la ruta más corta.""".format(len(ciudades), len(carreteras))
        
        self.mostrar_mensaje(mensaje)
        self.actualizar_grafo()
    
    def mostrar_mensaje(self, mensaje: str):
        self.text_resultados.delete(1.0, tk.END)
        self.text_resultados.insert(tk.END, mensaje)


def main():
    root = tk.Tk()
    app = AplicacionRutaMinima(root)
    root.mainloop()


if __name__ == "__main__":
    main()
