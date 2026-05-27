#Importamos de librerias
import tkinter as tk
from tkinter import messagebox as msg
import socket


#Importamos de scripts
from check.processcheck import checkout as cout
from games.ruleta import Ruleta as rule
from games.tragamonedas import Tragamonedas as trag
from games.poker import Poker as pok
from games.basegame import BaseGame as bg

class CasinoApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sindicato de Juego - Ubuntu Edition")
        self.root.geometry("600x500")
        self.nombre_usuario = ""
        self.monto_usuario = 0.0
        self.root.protocol("WM_DELETE_WINDOW", self.protocol_shutdown)
        self.servidor_host = "localhost"
        self.servidor_puerto = 12010
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)

        self.show_login_page()

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
        tk.Label(frame, text=f"Saldo: ${self.monto_usuario:.2f}", font=("Arial", 12, "bold"), fg="green").pack(pady=10)
        
        tk.Button(frame, text="Cambiar Servidor", bg="#2196F3", fg="white", command=self.cambiar_servidor).pack(fill="x", pady=5)

        juegos = ["Ruleta", "Poker", "Tragamonedas"]
        for i, juego in enumerate(juegos, 1):
            tk.Button(frame, text=f"Juego {i}: {juego}", width=30,
                      command=lambda j=juego: self.confirmar_juego(j)).pack(pady=2)

        tk.Button(frame, text="Volver al Inicio", bg="#f44336", fg="white",
                  command=self.show_login_page).pack(pady=20)
    
    def cambiar_servidor(self):
        self.clear_screen()
        frame = tk.Frame(self.main_container)
        frame.pack(pady=50)
        
        tk.Label(frame, text="CONFIGURAR SERVIDOR", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(frame, text="Host:").pack()
        self.entry_host = tk.Entry(frame)
        self.entry_host.insert(0, self.servidor_host)
        self.entry_host.pack(pady=5)
        
        tk.Label(frame, text="Puerto:").pack()
        self.entry_puerto = tk.Entry(frame)
        self.entry_puerto.insert(0, str(self.servidor_puerto))
        self.entry_puerto.pack(pady=5)
        
        tk.Button(frame, text="Guardar", bg="#4CAF50", fg="white", command=self.guardar_servidor).pack(fill="x", pady=5)
        tk.Button(frame, text="Volver", command=self.show_game_menu).pack(fill="x")
    
    def guardar_servidor(self):
        host = self.entry_host.get()
        try:
            puerto = int(self.entry_puerto.get())
        except ValueError:
            msg.showwarning("Error", "Puerto debe ser un número")
            return
        
        self.servidor_host = host
        self.servidor_puerto = puerto
        msg.showinfo("OK", f"Servidor actualizado: {host}:{puerto}")
        self.show_game_menu()


    def show_load_page(self):
        self.clear_screen()
        frame = tk.Frame(self.main_container)
        frame.pack(pady=50)
        tk.Label(frame, text="ACCESO A CUENTA", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(frame, text="Usuario:").pack()
        self.ent_user = tk.Entry(frame); self.ent_user.pack(pady=5)
        tk.Label(frame, text="Contrasena:").pack()
        self.ent_pass = tk.Entry(frame, show="*"); self.ent_pass.pack(pady=5)
        tk.Button(frame, text="Entrar", bg="#2196F3", fg="white", command=self.ejecutar_login).pack(fill="x", pady=10)
        tk.Button(frame, text="Regresar", command=self.show_login_page).pack(fill="x")

    # ── COMUNICACION CON BACK GO (puerto 12010) ──────────────────────────────

    def enviar_comando(self, comando):
        """Envia comando al backend Go y retorna la respuesta."""
        try:
            with socket.create_connection(('localhost', 12010), timeout=3) as s:
                s.sendall(comando.encode())
                return s.recv(4096).decode()
        except Exception as e:
            msg.showerror("Error de Red", f"No se pudo conectar con Go: {e}")
            return None

    def nueva_partida(self):
        nombre    = self.entry_nombre.get()
        pswd      = self.entry_pswd.get()
        monto_text = self.entry_monto.get()

        if not nombre or not monto_text or not pswd:
            msg.showwarning("Atencion", "Datos incompletos")
            return
        try:
            monto = float(monto_text)
        except ValueError:
            msg.showwarning("Atencion", "El monto debe ser un numero valido")
            return
        if monto <= 0:
            msg.showwarning("Atencion", "El monto debe ser mayor que cero")
            return

        respuesta = self.enviar_comando(f"REG|{nombre}|{pswd}|{monto:.2f}")
        if respuesta and respuesta.startswith("OK"):
            self.nombre_usuario = nombre
            self.monto_usuario  = monto
            self.show_game_menu()

    def ejecutar_login(self):
        user = self.ent_user.get()
        pwd  = self.ent_pass.get()
        if not user or not pwd:
            msg.showwarning("Error", "Debes llenar todos los campos")
            return

        respuesta = self.enviar_comando(f"LOG|{user}|{pwd}")
        if respuesta and respuesta.startswith("OK"):
            partes = respuesta.split("|")
            if len(partes) >= 2:
                self.nombre_usuario = user
                try:
                    self.monto_usuario = float(partes[1])
                except ValueError:
                    self.monto_usuario = 0.0
                self.show_game_menu()
            else:
                msg.showerror("Error de Acceso", "Respuesta inesperada del servidor")
        else:
            msg.showerror("Error de Acceso", "Skill Issue")

    def confirmar_juego(self, nombre_juego):
        self.clear_screen()
        frame = tk.Frame(self.main_container)
        frame.pack(pady=20)
        
        if nombre_juego == "Ruleta":
            rule(self.root, frame, self.nombre_usuario, self.monto_usuario, self.servidor_host, self.servidor_puerto, self.show_game_menu)
        elif nombre_juego == "Tragamonedas":
            trag(self.root, frame, self.nombre_usuario, self.monto_usuario, self.servidor_host, self.servidor_puerto, self.show_game_menu)
        elif nombre_juego == "Poker":
            pok(self.root, frame, self.nombre_usuario, self.monto_usuario, self.servidor_host, self.servidor_puerto, self.show_game_menu)

    def protocol_shutdown(self):
        if msg.askyesno("Salir", "Deseas cerrar el casino?"):
            self.root.quit()
            self.root.destroy()

    def actualizar_saldo(self, nuevo_saldo):
        self.monto_usuario = nuevo_saldo
        self.show_game_menu()


root = tk.Tk()
app = CasinoApp(root)
root.mainloop()