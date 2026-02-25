import tkinter as tk
from tkinter import messagebox as msg, ttk, simpledialog
import socket

#Instanciamos una clase para manejo eficiente y mas simple del frontend
class CasinoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sindicato de Juego - Ubuntu Edition")
        self.root.geometry("600x500")
        
        # Variables de sesión únicas
        self.nombre_usuario = ""
        self.monto_usuario = 0
        
        # Protocolo para evitar procesos zombies
        self.root.protocol("WM_DELETE_WINDOW", self.protocol_shutdown)
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)
        
        self.show_login_page()


    #FUncion para evitar sin impotar en que widget estemos, un proceso zombie, por no terminar bien el proceso
    def clear_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_login_page(self):
        self.clear_screen()
        frame = tk.Frame(self.main_container)
        frame.pack(pady=50)

        tk.Label(frame, text="BIENVENIDO AL CASINO", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(frame, text="Nombre:").pack()
        self.entry_nombre = tk.Entry(frame); self.entry_nombre.pack()

        tk.Label(frame, text="Password").pack()
        self.entry_pswd = tk.Entry(frame, show="*"); self.entry_pswd.pack()
        
        tk.Label(frame, text="Monto inicial:").pack()
        self.entry_monto = tk.Entry(frame); self.entry_monto.pack()

        tk.Button(frame, text="Nueva Partida", bg="#4CAF50", fg="white", command=self.nueva_partida).pack(fill="x", pady=5)
        tk.Button(frame, text="Cargar Partida", command=self.show_load_page).pack(fill="x", pady=5)
        tk.Button(frame, text="Salir", bg="#f44336", fg="white", command=self.protocol_shutdown).pack(fill="x", pady=5)

    def show_game_menu(self):
        self.clear_screen()
        frame = tk.Frame(self.main_container)
        frame.pack(pady=20)

        tk.Label(frame, text=f"Jugador: {self.nombre_usuario}", font=("Arial", 12)).pack()
        tk.Label(frame, text=f"Saldo: ${self.monto_usuario}", font=("Arial", 12, "bold"), fg="green").pack(pady=10)

        juegos = ["Ruleta", "Blackjack", "Tragamonedas", "Póker"]
        for i, juego in enumerate(juegos, 1):
            #Se usa una funcion lambda para mostrar los 4 juegos del arreglo, para eficientizar el juego
            tk.Button(frame, text=f"Juego {i}: {juego}", width=30, command=lambda j=juego: self.confirmar_juego(j)).pack(pady=2)

        tk.Button(frame, text="Volver al Inicio", bg="#f44336", fg="white", command=self.show_login_page).pack(pady=20)

    def show_load_page(self):
        self.clear_screen()
        frame = tk.Frame(self.main_container)
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        columns = ("id", "nombre", "monto")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID"); self.tree.heading("nombre", text="Nombre"); self.tree.heading("monto", text="Monto")
        self.tree.pack(fill="both", expand=True)

        self.populate_table()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Cargar Seleccionado", bg="#2196F3", fg="white", command=self.cargar_seleccion).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Regresar", command=self.show_login_page).pack(side="left", padx=5)

    # --- COMUNICACIÓN ---

    def enviar_comando(self, comando):
        """Función Maestra: Aquí se resuelve el tema de los bytes (.encode)"""
        try:
            with socket.create_connection(('172.29.72.140', 8080), timeout=2) as s:
                s.sendall(comando.encode()) # Recibe el comando de los botones
                return s.recv(4096).decode()
        except Exception as e:
            msg.showerror("Error de Red", f"No se pudo conectar con Go: {e}")
            return None

    def nueva_partida(self):
        nombre = self.entry_nombre.get()
        monto = self.entry_monto.get()
        pswd = self.entry_pswd.get()

        if not nombre or not monto or not pswd:
            msg.showwarning("Atención", "Datos incompletos")
            return

        # Enviamos comando REG al backend
        respuesta = self.enviar_comando(f"REG|{nombre}|{monto}|{pswd}")
        
        if respuesta and respuesta.startswith("OK"):
            self.nombre_usuario = nombre
            self.monto_usuario = monto
            self.show_game_menu()

    def populate_table(self):
        respuesta = self.enviar_comando("GET")
        if respuesta and respuesta != "EMPTY":
            # Limpiar tabla antes de llenar
            for i in self.tree.get_children(): self.tree.delete(i)
            
            for i, fila in enumerate(respuesta.split(";"), 1):
                datos = fila.split(",")
                if len(datos) >= 2:
                    self.tree.insert("", "end", values=(i, datos[0], datos[1]))

    def cargar_seleccion(self):
        """Versión PRO: Desafío de autenticación"""
        item = self.tree.selection()
        if not item: 
            msg.showwarning("Error", "Selecciona una partida")
            return

        datos_fila = self.tree.item(item)['values']
        nombre_sel = datos_fila[1]

        pwd = simpledialog.askstring("Validación", f"Password para {nombre_sel}:", show='*')
        
        if pwd:
            respuesta = self.enviar_comando(f"LOG|{nombre_sel}|{pwd}")
            if respuesta and respuesta.startswith("OK"):
                self.nombre_usuario = nombre_sel
                self.monto_usuario = respuesta.split("|")[1] # Go nos devuelve el saldo
                self.show_game_menu()
            else:
                msg.showerror("Skill Issue", "      Skill Issue        ")

    def confirmar_juego(self, nombre_juego):
        msg.showinfo("Entrando", f"Iniciando {nombre_juego}... ¡Buena suerte!")

    def protocol_shutdown(self):
        if msg.askyesno("Salir", "¿Deseas cerrar el casino?"):
            self.root.quit()
            self.root.destroy()

root = tk.Tk()
app = CasinoApp(root)
root.mainloop()