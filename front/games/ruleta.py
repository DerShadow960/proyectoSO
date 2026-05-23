import tkinter as tk
import math
import threading
from tkinter import messagebox as msg
from games.basegame import BaseGame


#Declaramos variables globales 
ORDEN_RULETA = [0, 28, 9, 26, 30, 11, 7, 20, 32, 17, 5, 22, 34, 15, 3, 24, 36, 13, 1, "00", 27, 10, 25, 29, 12, 8, 19, 31, 18, 6, 21, 33, 16, 4, 23, 35, 14, 2]
ROJOS_RULETA = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

class Ruleta(BaseGame):
    def __init__(self, root, frame, nom_user, sal_user, host, puerto):
        super().__init__(root, frame, nom_user, sal_user, host, puerto)
        self.root.geometry("1000x800")
        self.root = root
        self._monto_ruleta = sal_user
        self._ruleta_girando = False
        self._ruleta_angulo = 0.0
        self._apuestas_activas = {}   # {(tipo, valor): monto}

        tk.Label(frame, text="RULEVER", font=("Arial", 17, "bold"), fg="#c0392b").pack(pady=(6, 1))
        tk.Label(frame, text=f"Jugador: {nom_user}", font=("Arial", 10)).pack()
        self.lbl_saldo_ruleta = tk.Label(frame, text=f"Saldo: ${sal_user:.2f}", font=("Arial", 12, "bold"), fg="#27ae60")
        self.lbl_saldo_ruleta.pack(pady=1)

        contenedor = tk.Frame(frame); 
        contenedor.pack(fill="both", expand=True)
        CX, CY, R_OUT, R_IN = 200, 200, 185, 100
        self._cvs = tk.Canvas(contenedor, width=400, height=400, bg="#0a4a1a", highlightthickness=0)
        self._cvs.pack(side="left", padx=10)

        n = len(ORDEN_RULETA); seg = 360.0 / n
        self._sector_items = []
        for i, num in enumerate(ORDEN_RULETA):
            start = -(i * seg)
            color = ("#1e8c2e" if num in (0, "00") else "#c0392b" if num in ROJOS_RULETA else "#1a1a1a")
            arc_id = self._cvs.create_arc( CX-R_OUT, CY-R_OUT, CX+R_OUT, CY+R_OUT, start=start, extent=seg, fill=color, outline="gold", width=1, style="pie")
            mid = math.radians(-(i * seg + seg / 2))
            r_t = R_OUT * 0.78
            txt_id = self._cvs.create_text(CX + r_t * math.cos(mid), CY - r_t * math.sin(mid), text=str(num), font=("Arial", 6, "bold"), fill="white", angle=(i * seg + seg / 2))
            self._sector_items.append((arc_id, txt_id, num))

        self._cvs.create_oval(CX-R_IN, CY-R_IN, CX+R_IN, CY+R_IN, fill="#2c1810", outline="gold", width=3)
        self._cvs.create_text(CX, CY, text="CASINO", font=("Arial", 9, "bold"), fill="gold")
        self._cvs.create_polygon(CX-8, 10, CX+8, 10, CX, 26, fill="gold", outline="white")

        R_BOLA = (R_IN + R_OUT) // 2 + 20
        bx = CX + R_BOLA * math.cos(math.radians(-90))
        by = CY + R_BOLA * math.sin(math.radians(-90))
        self._bolita = self._cvs.create_oval(bx-5, by-5, bx+5, by+5, fill="white", outline="#cccccc", width=1)
        self._ruleta_r_bola = R_BOLA
        self._ruleta_cx=CX; self._ruleta_cy=CY
        self._ruleta_r_out=R_OUT; self._ruleta_r_in=R_IN; self._ruleta_seg=seg

        # Panel de apuestas
        panel = tk.Frame(contenedor, bg="#0a4a1a")
        panel.pack(side="left", fill="both", expand=True, padx=6)

        tk.Label(panel, text="TU APUESTA", font=("Arial", 11, "bold"), fg="gold", bg="#0a4a1a").pack(pady=(10, 2))
        mf = tk.Frame(panel, bg="#0a4a1a"); mf.pack()
        tk.Label(mf, text="$", font=("Arial", 13, "bold"), fg="white", bg="#0a4a1a").pack(side="left")
        self._ent_apuesta_ruleta = tk.Entry(mf, width=8, font=("Arial", 13))
        self._ent_apuesta_ruleta.insert(0, "10"); self._ent_apuesta_ruleta.pack(side="left")

        tk.Label(panel, text="-"*26, fg="#27ae60", bg="#0a4a1a").pack(pady=4)

        # Color
        tk.Label(panel, text="Color  (paga 2x)", font=("Arial", 10, "bold"), fg="#bdc3c7", bg="#0a4a1a").pack()
        cf = tk.Frame(panel, bg="#0a4a1a"); cf.pack(pady=2)
        tk.Button(cf, text="ROJO",  bg="#c0392b", fg="white", width=10, font=("Arial", 10, "bold"), command=lambda: self._preparar_apuesta("color", "rojo")).pack(side="left", padx=3)
        tk.Button(cf, text="NEGRO", bg="#2c3e50", fg="white", width=10, font=("Arial", 10, "bold"), command=lambda: self._preparar_apuesta("color", "negro")).pack(side="left", padx=3)

        # Par/Impar
        tk.Label(panel, text="Par / Impar  (paga 2x)", font=("Arial", 10, "bold"), fg="#bdc3c7", bg="#0a4a1a").pack(pady=(6,0))
        pf = tk.Frame(panel, bg="#0a4a1a"); pf.pack(pady=2)
        tk.Button(pf, text="PAR",   bg="#2980b9", fg="white", width=10, font=("Arial", 10, "bold"), command=lambda: self._preparar_apuesta("paridad", "par")).pack(side="left", padx=3)
        tk.Button(pf, text="IMPAR", bg="#8e44ad", fg="white", width=10, font=("Arial", 10, "bold"), command=lambda: self._preparar_apuesta("paridad", "nopar")).pack(side="left", padx=3)

        # Docena
        tk.Label(panel, text="Docena  (paga 3x)", font=("Arial", 10, "bold"), fg="#bdc3c7", bg="#0a4a1a").pack(pady=(6,0))
        df = tk.Frame(panel, bg="#0a4a1a"); df.pack(pady=2)
        for etq, val in [("1a 1-12","primera"),("2a 13-24","segunda"),("3a 25-36","tercera")]:
            tk.Button(df, text=etq, bg="#16a085", fg="white", width=9, font=("Arial", 9, "bold"), command=lambda v=val: self._preparar_apuesta("docena", v)).pack(side="left", padx=2)

        # Número exacto
        tk.Label(panel, text="Numero exacto  (paga 36x)", font=("Arial", 10, "bold"), fg="#bdc3c7", bg="#0a4a1a").pack(pady=(6,0))
        gf = tk.Frame(panel, bg="#0a4a1a"); gf.pack(pady=2)
        for idx, n in enumerate(["0","00"] + [str(x) for x in range(1,37)]):
            bg_n = "#1e8c2e" if n in ("0","00") else ("#c0392b" if int(n) in ROJOS_RULETA else "#1a1a1a")
            tk.Button(gf, text=n, bg=bg_n, fg="white", font=("Arial", 8, "bold"), width=4, height=1, command=lambda v=n: self._preparar_apuesta("numero", v)).grid(row=idx//6, column=idx%6, padx=1, pady=1)

        tk.Label(panel, text="-"*26, fg="#27ae60", bg="#0a4a1a").pack(pady=2)

        tk.Label(panel, text="APUESTAS ACTIVAS:", font=("Arial", 9, "bold"), fg="gold", bg="#0a4a1a").pack()
        self._lbl_apuestas_activas = tk.Label(panel, text="Ninguna", font=("Arial", 8), fg="#f39c12", bg="#0a4a1a", wraplength=220, justify="left")
        self._lbl_apuestas_activas.pack()
        tk.Button(panel, text="Limpiar apuestas", font=("Arial", 8), bg="#555", fg="white", command=self._limpiar_apuestas).pack(pady=2)

        self._btn_girar = tk.Button(panel, text="GIRAR!", bg="#e74c3c", fg="white", font=("Arial", 13, "bold"), width=18, height=2, command=self._girar_ruleta, state="disabled")
        self._btn_girar.pack(pady=4)
        self._lbl_resultado_ruleta = tk.Label(panel, text="Selecciona apuestas y monto", font=("Arial", 10), fg="#ecf0f1", bg="#145214", relief="ridge", width=30, pady=6, wraplength=220)
        self._lbl_resultado_ruleta.pack(pady=4)
        tk.Button(panel, text="<- Volver al Menu", command=lambda: [self.root.geometry("600x500"), self.show_game_menu()], bg="#7f8c8d", fg="white", font=("Arial", 10)).pack(pady=4)

    def _etiquetar(self, tipo, valor):
        if tipo == "color":   return f"Color {valor.capitalize()}"
        if tipo == "paridad": return f"{valor.capitalize()}"
        if tipo == "docena":  return {"primera":"Doc 1-12","segunda":"Doc 13-24","tercera":"Doc 25-36"}[valor]
        return f"Num {valor}"

    def _preparar_apuesta(self, tipo, valor):
        """Agrega la apuesta al dict con el monto actual del entry."""
        try:
            monto = float(self._ent_apuesta_ruleta.get())
        except ValueError:
            msg.showwarning("Monto invalido", "Ingresa un monto valido antes de seleccionar.")
            return
        if monto <= 0:
            msg.showwarning("Monto invalido", "El monto debe ser mayor que cero.")
            return

        self._apuestas_activas[(tipo, valor)] = monto  # sobreescribe si ya existe ese tipo+valor

        total = sum(self._apuestas_activas.values())
        lineas = [f"  {self._etiquetar(t,v)}: ${m:.2f}" for (t,v),m in self._apuestas_activas.items()]
        lineas.append(f"  ----------")
        lineas.append(f"  TOTAL: ${total:.2f}")
        self._lbl_apuestas_activas.config(text="\n".join(lineas))
        self._btn_girar.config(state="normal")

    def _limpiar_apuestas(self):
        self._apuestas_activas.clear()
        self._lbl_apuestas_activas.config(text="Ninguna")
        self._btn_girar.config(state="disabled")
        self._lbl_resultado_ruleta.config(text="Selecciona apuestas y monto", fg="#ecf0f1")

    def _girar_ruleta(self):
        """Manda cada apuesta al back Go en un hilo, luego anima con el numero real."""
        if self._ruleta_girando or not self._apuestas_activas:
            return

        total = sum(self._apuestas_activas.values())
        if total > self._monto_ruleta:
            msg.showwarning("Sin fondos",
                f"Total apostado ${total:.2f} supera tu saldo ${self._monto_ruleta:.2f}")
            return

        self._ruleta_girando = True
        self._btn_girar.config(state="disabled")
        self._lbl_resultado_ruleta.config(text="Consultando al servidor...", fg="#f39c12")

        apuestas_snap = dict(self._apuestas_activas)

        def _consultar():
            resultados = []
            for (tipo, valor), monto in apuestas_snap.items():
                resp = self.enviar_comando(
                    f"RULETA|{self.nombre_usuario}|{monto:.2f}|{valor}")
                resultados.append(((tipo, valor), monto, resp))
            self.root.after(0, lambda r=resultados: self._procesar_respuestas_ruleta(r))

        threading.Thread(target=_consultar, daemon=True).start()

    def _procesar_respuestas_ruleta(self, resultados):
        """Recibe lista de respuestas del back, acumula resultado y anima."""
        numero_ganador = None
        ganancia_total = 0.0
        errores = []
        ultimo_saldo = self._monto_ruleta

        for (tipo, valor), monto, resp in resultados:
            if resp is None:
                errores.append(f"{self._etiquetar(tipo,valor)}: sin respuesta")
                continue
            partes = resp.split("|")
            if partes[0] == "ERROR":
                errores.append(f"{self._etiquetar(tipo,valor)}: {partes[1] if len(partes)>1 else resp}")
                continue
            # OK|WIN/LOSE|payout|numero|nuevoSaldo
            if numero_ganador is None:
                numero_ganador = partes[3]   
            ultimo_saldo  = float(partes[4])   
            if partes[1] == "WIN":
                ganancia_total += float(partes[2]) - monto
            else:
                ganancia_total -= monto

        if numero_ganador is None:
            self._ruleta_girando = False
            self._btn_girar.config(state="normal")
            self._lbl_resultado_ruleta.config(
                text="Error: " + " | ".join(errores), fg="#e74c3c")
            return

        self._ruleta_resultado = {
            "numero":      numero_ganador,
            "ganancia":    ganancia_total,
            "nuevoSaldo":  ultimo_saldo,
            "errores":     errores,
        }

        try:
            num_key = "00" if numero_ganador == "00" else int(numero_ganador)
            idx_ganador = ORDEN_RULETA.index(num_key)
        except (ValueError, IndexError):
            idx_ganador = 0

        seg = self._ruleta_seg
        self._ruleta_destino = self._ruleta_angulo - (5*360) - (idx_ganador*seg + seg/2)
        self._ruleta_pasos = 0
        self._ruleta_total_pasos = 80
        self._lbl_resultado_ruleta.config(text="Girando...", fg="#f39c12")
        self._animar_ruleta()

    def _animar_ruleta(self):
        if self._ruleta_pasos >= self._ruleta_total_pasos:
            self._ruleta_girando = False
            self._btn_girar.config(state="normal")
            self._mostrar_resultado_ruleta()
            return

        t = self._ruleta_pasos / self._ruleta_total_pasos
        delta = (self._ruleta_destino - self._ruleta_angulo) / self._ruleta_total_pasos
        self._ruleta_angulo += delta * (1 + 2*(1-t))
        self._ruleta_pasos  += 1

        seg=self._ruleta_seg; CX=self._ruleta_cx; CY=self._ruleta_cy
        R_OUT=self._ruleta_r_out; R_IN=self._ruleta_r_in

        # Rotar sectores (rueda gira en sentido contrario)
        for i, (arc_id, txt_id, _) in enumerate(self._sector_items):
            start = self._ruleta_angulo - (i*seg)
            self._cvs.itemconfig(arc_id, start=start)
            mid = math.radians(start + seg/2)
            r_t = R_OUT * 0.78
            self._cvs.coords(txt_id, CX+r_t*math.cos(mid), CY-r_t*math.sin(mid))
            self._cvs.itemconfig(txt_id, angle=(-(start+seg/2))%360)


        angulo_bola = -self._ruleta_angulo * 1.6
        R_BOLA = self._ruleta_r_bola
        bx = CX + R_BOLA * math.cos(math.radians(angulo_bola))
        by = CY + R_BOLA * math.sin(math.radians(angulo_bola))
        self._cvs.coords(self._bolita, bx-5, by-5, bx+5, by+5)
        # La bolita cae hacia el interior al frenar
        caida = int(20 * t)   # se acerca al centro conforme frena
        R_BOLA_ACT = R_BOLA - caida
        bx = CX + R_BOLA_ACT * math.cos(math.radians(angulo_bola))
        by = CY + R_BOLA_ACT * math.sin(math.radians(angulo_bola))
        self._cvs.coords(self._bolita, bx-5, by-5, bx+5, by+5)

        self.root.after(16, self._animar_ruleta)

    def _mostrar_resultado_ruleta(self):
        r = self._ruleta_resultado
        numero     = r["numero"]
        ganancia   = r["ganancia"]
        nuevoSaldo = r["nuevoSaldo"]
        errores    = r["errores"]

        self.monto_usuario  = nuevoSaldo
        self._monto_ruleta  = nuevoSaldo
        self._lbl_saldo_ruleta.config(text=f"Saldo: ${nuevoSaldo:.2f}")
        self._limpiar_apuestas()

        signo = "+" if ganancia >= 0 else ""
        color = "#2ecc71" if ganancia >= 0 else "#e74c3c"
        texto = f"{'GANASTE!' if ganancia>=0 else 'Perdiste'}  {signo}${ganancia:.2f}\nNumero: {numero}"
        if errores:
            texto += "\n" + " | ".join(errores)
        self._lbl_resultado_ruleta.config(text=texto, fg=color)

        if nuevoSaldo <= 0:
            msg.showinfo("Sin fondos", "Te quedaste sin saldo!")
            self.root.geometry("600x500")
            self.show_game_menu()
