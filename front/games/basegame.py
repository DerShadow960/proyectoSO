import tkinter as tk
import socket
from tkinter import messagebox as msg

class BaseGame:
    def __init__(self, root, frame, nombre_usuario, monto_usuario, host, puerto):
        self.root = root
        self.frame = frame
        self.nombre_usuario = nombre_usuario
        self.monto_usuario = monto_usuario
        self.host = host
        self.puerto = int(puerto)
    
    def enviar_comando(self, comando):
        try:
            with socket.create_connection((self.host, self.puerto), timeout=3) as s:
                s.sendall(comando.encode())
                return s.recv(4096).decode()
        except Exception as e:
            msg.showerror("Error de Red", f"No se pudo conectar: {e}")
            return None