package main

import (
	"database/sql"
	"fmt"
	"math/rand"
	"net"
	"os"
	"strings"
	"time"

	"proyectoSO/games"

	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
)

func main() {
	rand.Seed(time.Now().UnixNano())

	if err := godotenv.Load("../.env"); err != nil {
		fmt.Println("Archivo .env no encontrado, usando variables de entorno")
	}

	host := os.Getenv("DB_HOST")
	port := os.Getenv("DB_PORT")
	user := os.Getenv("DB_USER")
	password := os.Getenv("DB_PASSWORD")
	dbname := os.Getenv("DB_NAME")

	if port == "" {
		port = "5432"
	}

	psgsql := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable", host, port, user, password, dbname)
	db, err := sql.Open("postgres", psgsql)
	if err != nil {
		fmt.Println("Error al iniciar servidor:", err)
		return
	}

	err = db.Ping()
	if err != nil {
		fmt.Println("Error, inicie el docker por Dios:", err)
	}
	fmt.Println("Conectado a la DB con éxito")

	ln, err := net.Listen("tcp", ":12010")
	if err != nil {
		fmt.Println("Error socket:", err)
		return
	}

	fmt.Println("Backend escuchando en :12010")
	for {
		conn, err := ln.Accept()
		if err != nil {
			continue
		}
		go handleConnection(conn, db)
	}
}

func handleConnection(conn net.Conn, db *sql.DB) {
	defer conn.Close()

	buffer := make([]byte, 1024)
	n, err := conn.Read(buffer)
	if err != nil {
		return
	}

	mensaje := string(buffer[:n])
	partes := strings.Split(mensaje, "|")

	if len(partes) == 0 {
		return
	}

	switch partes[0] {
	case "REG":
		registrar(conn, db, partes[1], partes[2], partes[3])
	case "LOG":
		login(conn, db, partes[1], partes[2])
	case "RULETA":
		if len(partes) < 4 {
			conn.Write([]byte("ERROR|Formato invalido"))
			return
		}
		games.HandleRuleta(conn, db, partes[1], partes[2], partes[3])
	case "TRAGAMONEDAS":
		if len(partes) < 3 {
			conn.Write([]byte("ERROR|Formato invalido"))
			return
		}
		games.HandleTragamonedas(conn, db, partes[1], partes[2])
	case "POKER":
		if len(partes) < 4 {
			conn.Write([]byte("ERROR|Formato invalido"))
			return
		}
		games.HandlePoker(conn, db, partes[1], partes[2], partes[3])
	default:
		conn.Write([]byte("ERROR|Comando no reconocido"))
	}
}

// ── REGISTRAR ────────────────────────────────────────────────────────────────

func registrar(conn net.Conn, db *sql.DB, nombre string, pswd string, monto string) {
	sqlquery := `INSERT INTO users (username, pswdhash, balance) VALUES ($1, $2, $3)`
	_, err := db.Exec(sqlquery, nombre, pswd, monto)
	if err != nil {
		fmt.Println("Error en el INSERT:", err)
		conn.Write([]byte("ERROR|Registro fallido"))
		return
	}
	fmt.Printf("Registro exitoso: %s\n", nombre)
	conn.Write([]byte("OK|Registrado"))
}

// ── LOGIN ────────────────────────────────────────────────────────────────────

func login(conn net.Conn, db *sql.DB, nombre string, pswd string) {
	var balance string
	query := "SELECT balance FROM users WHERE username = $1 AND pswdhash = $2"
	err := db.QueryRow(query, nombre, pswd).Scan(&balance)
	if err != nil {
		if err == sql.ErrNoRows {
			conn.Write([]byte("ERROR|Unauthorized"))
		} else {
			conn.Write([]byte("ERROR|DB_DOWN"))
		}
		return
	}
	conn.Write([]byte("OK|" + balance))
}
