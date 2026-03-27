package main

import (
	"database/sql"
	"fmt"
	"net"
	"os"
	"strings"

	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
)

func main() {

	error := godotenv.Load("../.env")
	if error != nil {
		fmt.Println("Error cargando el archivo .env")
	}

	host := os.Getenv("DB_HOST")
	port := os.Getenv("DB_PORT")
	user := os.Getenv("DB_USER")
	password := os.Getenv("DB_PASSWORD")
	dbname := os.Getenv("DB_NAME")

	psgsql := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable", host, port, user, password, dbname)
	db, err := sql.Open("postgres", psgsql)

	if err != nil {
		fmt.Println("Error al iniciar servidor, chequele mi compadre:", err)
		return
	}

	err = db.Ping()
	if err != nil {
		fmt.Println("Error, inicie el docker por Dios:", err)
	}
	fmt.Println("Conectado a la DB con éxito")
	ln, err := net.Listen("tcp", ":12010") // Tu puerto secreto
	if err != nil {
		fmt.Println("Error socket:", err)
		return
	}

	// 4. El ciclo infinito
	for {
		conn, err := ln.Accept()
		if err != nil {
			continue
		}
		go handleConnection(conn, db)
	}

}

func handleConnection(conn net.Conn, db *sql.DB) {
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
		// Formato: REG|nombre|passwordhash|monto
		registrar(conn, db, partes[1], partes[2], partes[3])
	case "LOG":
		// Formato: LOG|nombre|password
		login(conn, db, partes[1], partes[2])
	case "ALPHA":
		games(conn, db, "ALPHA")
	case "BETA":
		games(conn, db, "BETA")
	case "GAMMA":
		games(conn, db, "GAMMA")
	case "DELTA":
		games(conn, db, "DELTA")
	default:
		conn.Write([]byte("ERROR|Comando no reconocido"))
	}
}

// --- FUNCIONES DE LÓGICA ---

func registrar(conn net.Conn, db *sql.DB, nombre string, pswd string, monto string) {
	sqlquery := `INSERT INTO users (username, pswdhash, balance) VALUES ($1, $2, $3)`
	_, err := db.Exec(sqlquery, nombre, pswd, monto)

	if err != nil {
		fmt.Println("Error en el INSERT:", err) // Esto lo ves tú en la consola
		conn.Write([]byte("ERROR|Registro fallido"))
		return
	}

	fmt.Printf("Registro exitoso: %s\n", nombre)
	conn.Write([]byte("OK|Registrado"))
}

func login(conn net.Conn, db *sql.DB, nombre string, pswd string) {
	var balance string
	// El $1 y $2 aseguran que nadie haga SQL Injection
	query := "SELECT balance FROM users WHERE username = $1 AND pswdhash = $2"

	err := db.QueryRow(query, nombre, pswd).Scan(&balance)

	if err != nil {
		if err == sql.ErrNoRows {
			// No encontramos al usuario o la clave no coincide
			conn.Write([]byte("ERROR|Unauthorized"))
		} else {
			// Error de conexión a la DB, hay que activar el contenedor de la DB
			conn.Write([]byte("ERROR|DB_DOWN"))
		}
		return
	}
	conn.Write([]byte("OK|" + balance))
}

func games(conn net.Conn, db *sql.DB, game string) {

}
