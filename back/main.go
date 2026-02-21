package main

import (
	"fmt"
	"net"
	"os"
	"strings" // Necesario para separar el texto
)

func main() {
	// 1. Abrir el puerto 8080 para que Python se conecte
	ln, _ := net.Listen("tcp", ":8080")
	fmt.Println("Servidor del Casino iniciado en Ubuntu...")

	for {
		conn, _ := ln.Accept()
		go handleConnection(conn) // Uso de hilos/goroutines para el casino
	}
}

func handleConnection(conn net.Conn) {
	defer conn.Close()
	buffer := make([]byte, 1024)
	n, err := conn.Read(buffer)
	if err != nil {
		return
	}

	mensaje := string(buffer[:n]) // El mensaje llega como "Nombre, Monto"
	partes := strings.Split(mensaje, ",") // Separamos por la coma

	if len(partes) < 2 {
		fmt.Println("Datos incompletos recibidos")
		return 0
	}

	nombre := strings.TrimSpace(partes[0])
	monto := strings.TrimSpace(partes[1])

	// 2. Lógica de archivos .txt (Guardar partida) 
	// Usamos permisos Unix 0644 como pide la arquitectura base [cite: 7, 15]
	datos := fmt.Sprintf("%s, %s\n", nombre, monto)
	
	// Usamos os.OpenFile con modo APPEND para no borrar a los jugadores anteriores, y evitar cualquier error
	f, err := os.OpenFile("../files/partida.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println("Error al abrir archivo")
		return
	}
	defer f.Close()

	if _, err := f.WriteString(datos); err != nil {
		fmt.Println("Error al escribir")
	}

	fmt.Printf("Jugador %s con monto %s guardado con éxito\n", nombre, monto)
	conn.Write([]byte("Conexion exitosa. Datos guardados en servidor Unix."))
}


