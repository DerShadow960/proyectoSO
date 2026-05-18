import tkinter as tk


#Declaramos variables globales 
ORDEN_RULETA = [0, 28, 9, 26, 30, 11, 7, 20, 32, 17, 5, 22, 34, 15, 3, 24, 36, 13, 1, "00", 27, 10, 25, 29, 12, 8, 19, 31, 18, 6, 21, 33, 16, 4, 23, 35, 14, 2]

ROJOS_RULETA = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}


class Ruleta:
    def __init__ (self, frame, nom_user, sal_user):
        self.root.geometry("1000x800")
        self.monto_ruleta = sal_user
        self.ruleta_girando   = False
        self.ruleta_angulo    = 0.0
        self.apuestas_activas = {}   # {(tipo, valor): monto}

        tk.Label(frame, text="RULEVER", font=("Arial", 17, "bold"), fg="#c0392b").pack(pady=(6, 1))
        tk.Label(frame, text=f"Jugador: {nom_user}", font=("Arial", 10)).pack()
        self._lbl_saldo_ruleta = tk.Label(frame, text=f"Saldo: ${sal_user:.2f}", font=("Arial", 12, "bold"), fg="#27ae60")
        self._lbl_saldo_ruleta.pack(pady=1)

        contenedor = tk.Frame(frame); contenedor.pack(fill="both", expand=True)

