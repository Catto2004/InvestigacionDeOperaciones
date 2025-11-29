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
        self.crear_panel_aristas()
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
    
    def crear_panel_aristas(self):
        frame = ttk.LabelFrame(self.panel_izquierdo, text=" Gestion Manual", padding="10")
        frame.pack(fill=tk.X, pady=5)
        
        od_frame = ttk.Frame(frame)
        od_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(od_frame, text="Origen:").pack(side=tk.LEFT)
        self.combo_origen = ttk.Combobox(od_frame, width=6, state="readonly")
        self.combo_origen.pack(side=tk.LEFT, padx=3)
        
        ttk.Label(od_frame, text="Dest:").pack(side=tk.LEFT, padx=(5, 0))
        self.combo_destino = ttk.Combobox(od_frame, width=6, state="readonly")
        self.combo_destino.pack(side=tk.LEFT, padx=3)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="+ Camino", command=self.agregar_arista, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="- Camino", command=self.eliminar_arista, width=10).pack(side=tk.LEFT, padx=2)
    
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
        
        self.text_resultados = tk.Text(frame, height=10, width=40, font=('Consolas', 10))
        self.text_resultados.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Limpiar Grafo", command=self.limpiar_grafo).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Cargar Ejemplo", command=self.cargar_ejemplo).pack(side=tk.LEFT, padx=2)
    
    def crear_panel_grafo(self):
        frame = ttk.LabelFrame(self.panel_derecho, text=" Visualizacion del Grafo (Haz clic para interactuar)", padding="5")
        frame.pack(fill=tk.BOTH, expand=True)
        
        self.figura = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figura.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.figura, master=frame)
        self.canvas.draw()
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
        for combo in [self.combo_origen, self.combo_destino, self.combo_inicio, self.combo_fin]:
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
                                  node_color=colores_nodos, node_size=800,
                                  edgecolors='black', linewidths=2)
            
            nx.draw_networkx_labels(self.grafo.grafo, self.grafo.posiciones, ax=self.ax,
                                   font_size=12, font_weight='bold')
            
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
        self.ax.set_xlim(-0.1, 1.1)
        self.ax.set_ylim(-0.1, 1.1)
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
    
    def agregar_nodo(self):
        """Agrega nodo desde los campos de texto (metodo manual)."""
        nombre = simpledialog.askstring("Nuevo Nodo", "Nombre del nodo:")
        if nombre:
            nombre = nombre.strip().upper()
            if nombre in self.grafo.grafo.nodes():
                messagebox.showwarning("Advertencia", f"El nodo '{nombre}' ya existe")
                return
            self.grafo.agregar_nodo(nombre, 0.5, 0.5)
            self.mostrar_mensaje(f"Nodo '{nombre}' agregado")
            self.actualizar_grafo()
    
    def eliminar_nodo(self):
        """Elimina nodo seleccionado en combo."""
        nombre = self.combo_origen.get()
        if not nombre:
            messagebox.showwarning("Advertencia", "Seleccione un nodo en 'Origen'")
            return
        
        self.grafo.eliminar_nodo(nombre)
        self.camino_actual = []
        self.mostrar_mensaje(f"Nodo '{nombre}' eliminado")
        self.actualizar_grafo()
    
    def agregar_arista(self):
        origen = self.combo_origen.get()
        destino = self.combo_destino.get()
        
        if not origen or not destino:
            messagebox.showwarning("Advertencia", "Seleccione origen y destino")
            return
        
        if origen == destino:
            messagebox.showwarning("Advertencia", "Origen y destino deben ser diferentes")
            return
        
        try:
            peso = float(self.entry_peso.get())
        except ValueError:
            messagebox.showwarning("Advertencia", "Ingrese un peso valido")
            return
        
        bidireccional = self.var_bidireccional.get()
        self.grafo.agregar_arista(origen, destino, peso, bidireccional)
        
        direccion = "<->" if bidireccional else "->"
        self.mostrar_mensaje(f"Camino agregado: {origen} {direccion} {destino} (peso: {peso})")
        self.actualizar_grafo()
    
    def eliminar_arista(self):
        origen = self.combo_origen.get()
        destino = self.combo_destino.get()
        
        if not origen or not destino:
            messagebox.showwarning("Advertencia", "Seleccione origen y destino")
            return
        
        self.grafo.eliminar_arista(origen, destino)
        self.camino_actual = []
        
        self.mostrar_mensaje(f"Camino eliminado: {origen} -> {destino}")
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
            nombre_algo = "BELLMAN-FORD"
        
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
    
    def mostrar_mensaje(self, mensaje: str):
        self.text_resultados.delete(1.0, tk.END)
        self.text_resultados.insert(tk.END, mensaje)


def main():
    root = tk.Tk()
    app = AplicacionRutaMinima(root)
    root.mainloop()


if __name__ == "__main__":
    main()
