import tkinter as tk
import tkinter as tk
from tkinter import messagebox as msg, ttk, simpledialog
import socket
import threading


class checkout():
    def __init__(self, root):
        self.root = root
        self.root.title("Sindicato de Juego - Ubuntu Edition")
        self.root.geometry("600x500")

        self.root.protocol("WM_DELETE_WINDOW", self.protocol_shutdown)
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)
        self.SERVICIOS = [("Backend Go",    "localhost", 12010), ("Base de datos", "localhost", 5432)]

        self.abrir_monitor()

    def abrir_monitor(self):
        win = tk.Toplevel(self.root)
        win.title("Monitor de Servicios")
        win.geometry("500x300")
        win.resizable(False, False)
        win.configure(bg="#1a1a2e")
        win.protocol("WM_DELETE_WINDOW", win.withdraw)
        self.monitor_win = win
        tk.Label(win, text="ESTADO DE SERVICIOS", font=("Courier", 12, "bold"), fg="#e2b96f", bg="#1a1a2e").pack(pady=(12, 6))
        self.mon_labels = {}
        for nombre, host, puerto in self.SERVICIOS:
            fila = tk.Frame(win, bg="#1a1a2e"); fila.pack(fill="x", padx=18, pady=3)
            tk.Label(fila, text=f"{nombre:<18}", font=("Courier", 10), fg="#aaaaaa", bg="#1a1a2e", width=18, anchor="w").pack(side="left")
            lbl = tk.Label(fila, text="...", font=("Courier", 10, "bold"), fg="#888888", bg="#1a1a2e", width=10, anchor="w")
            lbl.pack(side="left")
            self.mon_labels[nombre] = lbl
        self.lbl_mon_hora = tk.Label(win, text="Actualizando...", font=("Courier", 8), fg="#555577", bg="#1a1a2e")
        self.lbl_mon_hora.pack(pady=4)
        tk.Button(win, text="Refrescar", font=("Courier", 9), bg="#2d2d4e", fg="#e2b96f", relief="flat", command=self.chequear_servicios).pack(pady=4)
        self.chequear_servicios()


    def ping(self, host, puerto):
        try:
            with socket.create_connection((host, puerto), timeout=1.5):
                return True
        except Exception:
            return False

    def chequear_servicios(self):
        def worker():
            res = {n: self.ping(h, p) for n, h, p in self.SERVICIOS}
            self.root.after(0, lambda: self.actualizar_monitor(res))
        threading.Thread(target=worker, daemon=True).start()
        self.root.after(5000, self.chequear_servicios)

    def actualizar_monitor(self, resultados):
        import datetime
        for nombre, estado in resultados.items():
            lbl = self.mon_labels.get(nombre)
            if lbl:
                lbl.config(text="UP  ●" if estado else "DOWN ●", fg="#2ecc71" if estado else "#e74c3c")
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        caido = [n for n, v in resultados.items() if not v]
        if caido:
            self.lbl_mon_hora.config(
                text=f"[!] CAIDO: {', '.join(caido)} — {hora}", fg="#e74c3c")
        else:
            self._lbl_mon_hora.config(
                text=f"Ultimo chequeo: {hora}  (cada 5s)", fg="#555577")

    def protocol_shutdown(self):
        if msg.askyesno("Salir", "Deseas cerrar el casino?"):
            self.root.quit()
            self.root.destroy()



#rooter = tk.Tk()
#app = checkout(rooter)
#rooter.mainloop()