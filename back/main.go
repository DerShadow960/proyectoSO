package main

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"strings"
	"sync"
)

// Mutex: El "semáforo" que evita que dos hilos choquen al tocar el archivo.
var mu sync.Mutex

const dbPath = "../files/partida.txt"

func main() {
	// Iniciamos el servidor en el puerto 8080
	ln, err := net.Listen("tcp", ":8080")
	if err != nil {
		fmt.Println("Error al iniciar servidor:", err)
		return
	}
	fmt.Println("Servidor Casino Omen iniciado en Ubuntu...")
	fmt.Println("Esperando conexiones del Front-end...")

	for {
		// Aceptamos una conexión (bloqueante hasta que alguien se conecte)
		conn, err := ln.Accept()
		if err != nil {
			continue
		}
		// Lanzamos una Goroutine: Es un hilo ligero que se encarga del cliente
		// Esto permite que 100 personas jueguen al mismo tiempo.
		go handleConnection(conn)
	}
}

func handleConnection(conn net.Conn) {
	defer conn.Close() // Cerramos el socket al terminar (evita procesos zombie de red)

	buffer := make([]byte, 1024)
	n, err := conn.Read(buffer)
	if err != nil {
		return
	}

	// Recibimos el mensaje y lo separamos por el delimitador "|"
	mensaje := string(buffer[:n])
	partes := strings.Split(mensaje, "|")

	if len(partes) == 0 {
		return
	}

	comando := partes[0]

	// RUTEO: ¿Qué quiere el usuario?
	switch comando {
	case "REG":
		// Formato: REG|nombre|monto|password
		registrar(conn, partes[1], partes[2], partes[3])
	case "LOG":
		// Formato: LOG|nombre|password
		login(conn, partes[1], partes[2])
	case "GET":
		// Formato: GET
		enviarLista(conn)
	default:
		conn.Write([]byte("ERROR|Comando no reconocido"))
	}
}

// --- FUNCIONES DE LÓGICA ---

func registrar(conn net.Conn, nombre, monto, pswd string) {
	mu.Lock() // SECCIÓN CRÍTICA: Nadie más entra aquí hasta que terminemos
	defer mu.Unlock()

	datos := fmt.Sprintf("%s,%s,%s\n", nombre, monto, pswd)
	f, err := os.OpenFile(dbPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		conn.Write([]byte("ERROR|No se pudo abrir la BD"))
		return
	}
	defer f.Close()

	f.WriteString(datos)
	fmt.Printf("Registro exitoso: %s\n", nombre)
	conn.Write([]byte("OK|Registrado"))
}

func login(conn net.Conn, nombre, pswd string) {
	mu.Lock()
	defer mu.Unlock()

	f, err := os.Open(dbPath)
	if err != nil {
		conn.Write([]byte("ERROR|Sin base de datos"))
		return
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		linea := scanner.Text()
		datos := strings.Split(linea, ",")
		// datos[0]=nombre, datos[1]=monto, datos[2]=password
		if datos[0] == nombre && datos[2] == pswd {
			fmt.Printf("Acceso concedido: %s\n", nombre)
			conn.Write([]byte("OK|" + datos[1])) // Mandamos OK y el saldo
			return
		}
	}
	conn.Write([]byte("DENIED|Credenciales incorrectas"))
}

func enviarLista(conn net.Conn) {
	mu.Lock()
	defer mu.Unlock()

	f, err := os.Open(dbPath)
	if err != nil {
		conn.Write([]byte("EMPTY"))
		return
	}
	defer f.Close()

	var acumulado []string
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		linea := scanner.Text()
		datos := strings.Split(linea, ",")
		// Mandamos solo Nombre y Monto por seguridad
		if len(datos) >= 2 {
			acumulado = append(acumulado, fmt.Sprintf("%s,%s", datos[0], datos[1]))
		}
	}

	// Unimos todo con ";" para que Python sepa dónde termina cada fila
	respuesta := strings.Join(acumulado, ";")
	if respuesta == "" {
		conn.Write([]byte("EMPTY"))
	} else {
		conn.Write([]byte(respuesta))
	}
}
