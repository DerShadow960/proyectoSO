package main

import (
	"database/sql"
	"fmt"
	"math/rand"
	"net"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
)

// Números rojos de la ruleta americana
var numerosRojos = map[int]bool{
	1: true, 3: true, 5: true, 7: true, 9: true, 12: true, 14: true,
	16: true, 18: true, 19: true, 21: true, 23: true, 25: true, 27: true,
	30: true, 32: true, 34: true, 36: true,
}

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

	psgsql := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)
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
		// REG|nombre|password|monto
		registrar(conn, db, partes[1], partes[2], partes[3])
	case "LOG":
		// LOG|nombre|password
		login(conn, db, partes[1], partes[2])
	case "RULETA":
		// RULETA|usuario|monto|opcion
		if len(partes) < 4 {
			conn.Write([]byte("ERROR|Formato invalido"))
			return
		}
		ruleta(conn, db, partes[1], partes[2], partes[3])
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

// ── RULETA ───────────────────────────────────────────────────────────────────
// Protocolo: RULETA|usuario|monto|opcion
// Opcion: "rojo","negro","par","impar","primera","segunda","tercera","0".."36","00"
// Respuesta: OK|WIN|payout|numero  o  OK|LOSE|0|numero  o  ERROR|motivo

func ruleta(conn net.Conn, db *sql.DB, usuario string, montoStr string, opcion string) {
	// Parsear monto
	monto, err := strconv.ParseFloat(montoStr, 64)
	if err != nil || monto <= 0 {
		conn.Write([]byte("ERROR|Monto invalido"))
		return
	}

	// Verificar saldo
	var saldoActual float64
	err = db.QueryRow("SELECT balance FROM users WHERE username = $1", usuario).Scan(&saldoActual)
	if err != nil {
		conn.Write([]byte("ERROR|Usuario no encontrado"))
		return
	}
	if monto > saldoActual {
		conn.Write([]byte("ERROR|Saldo insuficiente"))
		return
	}

	// Girar la ruleta: 0-36 son normales, 37 = "00"
	spin := rand.Intn(38) // 0..37

	// Determinar si ganó y cuánto
	win := false
	payout := 0.0
	spinStr := strconv.Itoa(spin)
	if spin == 37 {
		spinStr = "00"
	}

	switch opcion {
	case "rojo":
		win = numerosRojos[spin]
		payout = monto * 2
	case "negro":
		win = spin > 0 && spin != 37 && !numerosRojos[spin]
		payout = monto * 2
	case "par":
		win = spin > 0 && spin != 37 && spin%2 == 0
		payout = monto * 2
	case "nopar":
		win = spin > 0 && spin != 37 && spin%2 != 0
		payout = monto * 2
	case "primera":
		win = spin >= 1 && spin <= 12
		payout = monto * 3
	case "segunda":
		win = spin >= 13 && spin <= 24
		payout = monto * 3
	case "tercera":
		win = spin >= 25 && spin <= 36
		payout = monto * 3
	default:
		// Número exacto: "0", "00", "1".."36"
		if opcion == spinStr {
			win = true
			payout = monto * 36
		}
	}

	// Calcular nuevo saldo
	var nuevoSaldo float64
	if win {
		nuevoSaldo = saldoActual - monto + payout
	} else {
		nuevoSaldo = saldoActual - monto
	}

	// Actualizar saldo en DB
	_, err = db.Exec("UPDATE users SET balance = $1 WHERE username = $2", nuevoSaldo, usuario)
	if err != nil {
		conn.Write([]byte("ERROR|No se pudo actualizar saldo"))
		return
	}

	// Registrar en gamelogs
	resultado := "loss"
	if win {
		resultado = "win"
	}
	db.Exec(`INSERT INTO gamelogs (userid, gametype, betamount, result)
		SELECT id, 'ruleta', $1, $2 FROM users WHERE username = $3`,
		monto, resultado, usuario)

	// Responder al front
	fmt.Printf("Ruleta — %s aposto $%.2f a '%s' → numero %s → %s (saldo: $%.2f)\n",
		usuario, monto, opcion, spinStr, resultado, nuevoSaldo)

	if win {
		conn.Write([]byte(fmt.Sprintf("OK|WIN|%.2f|%s|%.2f", payout, spinStr, nuevoSaldo)))
	} else {
		conn.Write([]byte(fmt.Sprintf("OK|LOSE|0|%s|%.2f", spinStr, nuevoSaldo)))
	}
}