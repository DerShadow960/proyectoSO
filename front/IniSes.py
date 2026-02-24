import tkinter as tk
from tkinter import messagebox as msg
from tkinter import ttk  # Para la tabla (Treeview)
import socket

class CasinoApp:
    def __init__(self, root):
        # Instanciamos los widget para empezar a pintar/modificar/ 
        self.root = root
        self.root.title("Sindicato de Juego - Ubuntu Edition")
        self.root.geometry("600x500")
        
        # Datos del jugador actual (Estado de la sesión)
        self.nombre_usuario = ""
        self.monto_usuario = 0
        
        # PROTOCOLO ANTIZOMBI: Si cierran la ventana de la X, matamos todo, evitamos procesos zombies.
        self.root.protocol("WM_DELETE_WINDOW", self.protocol_shutdown)
        
        # Contenedor principal donde "suichearemos" las páginas
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)
        
        self.show_login_page()

    # FUNCIONES PARA LA NAVEGACION DEL USUARIO

    def clear_screen(self):
        # """Limpia el contenedor principal para cargar una nueva vista."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_login_page(self):
        # """Página 1: Login / Inicio"""
        self.clear_screen()
        frame = tk.Frame(self.main_container)
        frame.pack(pady=50)

        tk.Label(frame, text="BIENVENIDO AL CASINO", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(frame, text="Nombre:").pack()
        self.entry_nombre = tk.Entry(frame)
        self.entry_nombre.pack()

        tk.Label(frame, text="Monto inicial:").pack()
        self.entry_monto = tk.Entry(frame)
        self.entry_monto.pack()

        # Uso de funciones lambda: Permiten pasar argumentos a una función en el command
        # sin que se ejecute la función inmediatamente al cargar el programa.
        tk.Button(frame, text="Nueva Partida", bg="#4CAF50", fg="white", command=self.nueva_partida).pack(fill="x", pady=5)
        tk.Button(frame, text="Cargar Partida", command=self.show_load_page).pack(fill="x", pady=5)
        tk.Button(frame, text="Salir", bg="#f44336", fg="white", command=self.protocol_shutdown).pack(fill="x", pady=5)

    def show_game_menu(self):
        # """Página 2: Menú de Juegos (Dashboard)"""
        self.clear_screen()
        frame = tk.Frame(self.main_container)
        frame.pack(pady=20)

        # Mostrar info del jugador
        tk.Label(frame, text=f"Jugador: {self.nombre_usuario}", font=("Arial", 12)).pack()
        tk.Label(frame, text=f"Saldo: ${self.monto_usuario}", font=("Arial", 12, "bold"), fg="green").pack(pady=10)

        tk.Label(frame, text="Seleccione un Juego:", font=("Arial", 14)).pack(pady=10)

        # Botones de juegos con confirmación
        juegos = ["Ruleta", "Blackjack", "Tragamonedas", "Póker"]
        for i, juego in enumerate(juegos, 1):
            # Usamos lambda j=juego para "congelar" el valor del nombre del juego en el loop
            tk.Button(frame, text=f"Juego {i}: {juego}", width=30, command=lambda j=juego: self.confirmar_juego(j)).pack(pady=2)

        tk.Button(frame, text="Volver al Inicio", bg="#f44336", fg="white", command=self.show_login_page).pack(pady=20)

    def show_load_page(self):
        # """Página 3: Cargar Partida con Tabla (Treeview)"""
        self.clear_screen()
        frame = tk.Frame(self.main_container)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        tk.Label(frame, text="PARTIDAS GUARDADAS", font=("Arial", 14, "bold")).pack(pady=10)

        # Configuración de la tabla
        columns = ("id", "nombre", "monto")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre del Jugador")
        self.tree.heading("monto", text="Monto Apostado")
        
        self.tree.pack(fill="both", expand=True)

        # Llenar la tabla leyendo el archivo (Camino A)
        self.populate_table()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Cargar Seleccionado", bg="#2196F3", fg="white", command=self.cargar_seleccion).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Regresar", command=self.show_login_page).pack(side="left", padx=5)

    # PATYE DE CONECTAR DE FORMA BIDIRECIONAL EL BACK CON EL FRONT

    def nueva_partida(self):
        # """Valida, envía datos al backend y entra al casino."""
        nombre = self.entry_nombre.get()
        monto = self.entry_monto.get()

        if not nombre or not monto:
            msg.showwarning("Atención", "Llena todos los campos")
            return

        # Conexión al backend (Go)
        try:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente.settimeout(2)
            cliente.connect(('localhost', 8080))
            cliente.send(f"{nombre}, {monto}".encode())
            cliente.close()
            
            # Guardamos en la sesión local
            self.nombre_usuario = nombre
            self.monto_usuario = monto
            self.show_game_menu()
        except:
            msg.showerror("Error", "El servidor Go no responde. ¿Lo encendiste?")

    def confirmar_juego(self, nombre_juego):
        # """Pide confirmación antes de entrar a un juego."""
        msg.showinfo("Entrando", f"Iniciando {nombre_juego}... ¡Buena suerte!")
        

    def populate_table(self):
        # """Lee el txt y llena la tabla del front."""
        try:
            with open("../files/partida.txt", "r") as f:
                for i, linea in enumerate(f, 1):
                    datos = linea.strip().split(",")
                    if len(datos) == 2:
                        # Insertamos en la tabla de Tkinter
                        self.tree.insert("", "end", values=(i, datos[0], datos[1]))
        except FileNotFoundError:
            msg.showinfo("Info", "No hay partidas guardadas todavía.")

    def cargar_seleccion(self):
        # """Obtiene el dato de la fila seleccionada y carga el juego."""
        selected_item = self.tree.selection()
        if not selected_item:
            msg.showwarning("Error", "Selecciona una fila primero")
            return
        
        item_data = self.tree.item(selected_item)['values']
        self.nombre_usuario = item_data[1]
        self.monto_usuario = item_data[2]
        self.show_game_menu()

    def protocol_shutdown(self):
        # """Protocolo de cierre limpio para evitar procesos zombis."""
        if msg.askyesno("Salir", "¿Deseas cerrar el casino?"):
            self.root.quit() # Detiene el mainloop
            self.root.destroy() # Destruye la ventana de la memoria


root = tk.Tk()
app = CasinoApp(root)
root.mainloop()