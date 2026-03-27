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

        juegos = ["Ruleta", "21/Blackjack", "Tragamonedas", "Póker", "Pesca"]
        for i, juego in enumerate(juegos, 1):
            #Se usa una funcion lambda para mostrar los 5 juegos del arreglo, para eficientizar el juego
            tk.Button(frame, text=f"Juego {i}: {juego}", width=30, command=lambda j=juego: self.confirmar_juego(j)).pack(pady=2)

        tk.Button(frame, text="Volver al Inicio", bg="#f44336", fg="white", command=self.show_login_page).pack(pady=20)

    def show_load_page(self):
        self.clear_screen()
        frame = tk.Frame(self.main_container)
        frame.pack(pady=50)

        tk.Label(frame, text="ACCESO A CUENTA", font=("Arial", 16, "bold")).pack(pady=10)    
        tk.Label(frame, text="Usuario:").pack()
        self.ent_user = tk.Entry(frame)
        self.ent_user.pack(pady=5)

        tk.Label(frame, text="Contraseña:").pack()
        self.ent_pass = tk.Entry(frame, show="*")
        self.ent_pass.pack(pady=5)

        tk.Button(frame, text="Entrar", bg="#2196F3", fg="white", command=self.ejecutar_login).pack(fill="x", pady=10)
        tk.Button(frame, text="Regresar", command=self.show_login_page).pack(fill="x")

    # --- COMUNICACIÓN ---

    def enviar_comando(self, comando):
        """Función Maestra: Aquí se resuelve el tema de los bytes (.encode)"""
        try:
            with socket.create_connection(('localhost', 12010), timeout=2) as s:
                s.sendall(comando.encode()) # Recibe el comando de los botones
                return s.recv(4096).decode()
        except Exception as e:
            msg.showerror("Error de Red", f"No se pudo conectar con Go: {e}")
            return None

    def nueva_partida(self):
        nombre = self.entry_nombre.get()
        pswd = self.entry_pswd.get()
        monto = self.entry_monto.get()

        if not nombre or not monto or not pswd:
            msg.showwarning("Atención", "Datos incompletos")
            return

        # Enviamos comando REG al backend
        respuesta = self.enviar_comando(f"REG|{nombre}|{pswd}|{monto}")
        
        if respuesta and respuesta.startswith("OK"):
            self.nombre_usuario = nombre
            self.monto_usuario = monto
            self.show_game_menu()

    def ejecutar_login(self):
        user = self.ent_user.get()
        pwd = self.ent_pass.get()

        if not user or not pwd:
            msg.showwarning("Error", "Debes llenar todos los campos")
            return

        # Enviamos el comando LOG al Backend
        respuesta = self.enviar_comando(f"LOG|{user}|{pwd}")
    
        if respuesta and respuesta.startswith("OK"):
            self.nombre_usuario = user
            self.monto_usuario = respuesta.split("|")[1]
            self.show_game_menu()
        else:
            # IMPORTANTE: No decimos qué falló, solo que no entró
            msg.showerror("Error de Acceso", "Skill Issue")
    
    def confirmar_juego(self, nombre_juego):
        # El usuario ingresa a un juego, se le muestra un mensaje de bienvenida
        posjuegos = ["Ruleta", "21/Blackjack", "Tragamonedas", "Póker", "Pesca"]
         
        if nombre_juego == "21/Blackjack" or nombre_juego == "Póker": 
            return self.enviar_comando("CASE|ALPHA")
        
        if nombre_juego == "Ruleta":
            return self.enviar_comando("CASE|BETA")
        
        elif nombre_juego == "Tragamonedas":
            return self.enviar_comando("CASE|GAMMA")

        elif nombre_juego == "Pesca":
            return self.enviar_comando("CASE|DELTA")
        else:
            msg.showerror("Error", "Juego no reconocido")
            return 

    def iniciar_juego(self, juego):
        return juego



    def protocol_shutdown(self):
        if msg.askyesno("Salir", "¿Deseas cerrar el casino?"):
            self.root.quit()
            self.root.destroy()

root = tk.Tk()
app = CasinoApp(root)
root.mainloop()