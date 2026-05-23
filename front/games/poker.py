import tkinter as tk
from tkinter import messagebox as msg
import threading
from games.basegame import BaseGame

class Poker(BaseGame):
    def __init__(self, root, frame, nombre_usuario, monto_usuario, host, puerto):
        super().__init__(root, frame, nombre_usuario, monto_usuario, host, puerto)
        self.monto = monto_usuario
        self.vs_cpu = True
        
        tk.Label(frame, text="POKER", font=("Arial", 17, "bold"), fg="#c0392b").pack(pady=10)
        tk.Label(frame, text=f"Jugador: {nombre_usuario}", font=("Arial", 10)).pack()
        self.lbl_saldo = tk.Label(frame, text=f"Saldo: ${monto_usuario:.2f}", font=("Arial", 12, "bold"), fg="#27ae60")
        self.lbl_saldo.pack(pady=5)
        
        tk.Label(frame, text="Monto a apostar:", font=("Arial", 10)).pack()
        self.entry_monto = tk.Entry(frame, width=10)
        self.entry_monto.insert(0, "10")
        self.entry_monto.pack()
        
        tf = tk.Frame(frame); tf.pack(pady=5)
        tk.Button(tf, text="RAISE", bg="#2980b9", fg="white", width=10, command=lambda: self.jugar("RAISE")).pack(side="left", padx=5)
        tk.Button(tf, text="CALL", bg="#27ae60", fg="white", width=10, command=lambda: self.jugar("CALL")).pack(side="left", padx=5)
        tk.Button(tf, text="FOLD", bg="#e74c3c", fg="white", width=10, command=lambda: self.jugar("FOLD")).pack(side="left", padx=5)
        
        self.lbl_resultado = tk.Label(frame, text="", font=("Arial", 11), fg="#2ecc71")
        self.lbl_resultado.pack(pady=10)
        
        tk.Button(frame, text="<- Volver", command=self.volver, bg="#7f8c8d", fg="white").pack(pady=5)
    
    def jugar(self, accion):
        try:
            monto = float(self.entry_monto.get())
        except ValueError:
            msg.showwarning("Error", "Ingresa un monto válido")
            return
        
        if monto > self.monto:
            msg.showwarning("Error", "Saldo insuficiente")
            return
        
        self.lbl_resultado.config(text="Jugando...", fg="#f39c12")
        threading.Thread(target=self._jugar_thread, args=(monto, accion), daemon=True).start()
    
    def _jugar_thread(self, monto, accion):
        resp = self.enviar_comando(f"POKER|{self.nombre_usuario}|{monto:.2f}|{accion}")
        self.root.after(0, lambda: self._mostrar_resultado(resp, accion))
    
    def _mostrar_resultado(self, resp, accion):
        if not resp:
            return
        
        partes = resp.split("|")
        if partes[0] == "ERROR":
            self.lbl_resultado.config(text=f"Error: {partes[1]}", fg="#e74c3c")
            return
        
        estado = partes[1]
        saldo = float(partes[3])
        self.monto = saldo
        self.lbl_saldo.config(text=f"Saldo: ${saldo:.2f}")
        
        if estado == "WIN":
            self.lbl_resultado.config(text=f"¡GANASTE! ({accion})", fg="#2ecc71")
        else:
            self.lbl_resultado.config(text=f"Perdiste... ({accion})", fg="#e74c3c")
        
        if saldo <= 0:
            msg.showinfo("Sin fondos", "Te quedaste sin saldo!")
            self.volver()
    
    def volver(self):
        for widget in self.frame.winfo_children():
            widget.destroy()