import tkinter.messagebox as msg
import tkinter as tk
import socket



def goconn_upload_pinfo():
    try:
        # Creamos el socket para hablar con el backend
        # socket.AF_INET--- Comando usado para indicar el uso del protocolo de internet version 4
        # socket.SOCK_STREAM--- Tipo de socket que usa el protoco TCP (Transmision Control Protocol), 
        #                           se usa para la transmicion de datos, de forma segura y estable
    
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.settimeout(2) # Si en 2 segundos no conecta, falla
        cliente.connect(('localhost', 8080))
        
        mensaje = f"{entry_nombre.get()}, {entry_monto.get()}"
        cliente.send(mensaje.encode())
        
        # Recibimos confirmación del servidor
        respuesta = cliente.recv(1024).decode()
        msg.showinfo("Servidor dice:", respuesta)
        
        cliente.close()
    except Exception as e:
        msg.showerror("Error", "No se pudo conectar con el servidor del Casino")

def loadgame():
    res = msg.askyesno("¿Cargar partida?", "Seguro?")
    if res:
        app.withdraw()
        gamecon = tk.Toplevel()
        gamecon.title("Menu de juegos")
        gamecon.geometry("500x300+100+100")
    elif not res:
        pass


def shutdown():
    s = msg.askyesno("¿TE VAS?", "¿Me abandonas?")
    if s:
        close_all_windows()
    elif not s:
        show_happy()        


def close_all_windows():
    app.destroy()

def show_happy():
    msg.showinfo("Yeah", "Gracias por no irte")

app = tk.Tk()
app.title("Cliente Casino")
app.geometry("500x300+100+100")


l_nombre = tk.Label(app, text="Nombre:").pack()
pnom = entry_nombre = tk.Entry(app)
entry_nombre.pack()

l_monto = tk.Label(app, text="Monto a iniciar:").pack()
pmon = entry_monto = tk.Entry(app)
entry_monto.pack()

tk.Button(app, text="Nueva Partida", command= goconn_upload_pinfo).pack()
tk.Button(app, text="Cargar Partida", command= loadgame).pack()
tk.Button(app, text="Guardar y Salir", command= shutdown).pack()



app.mainloop()