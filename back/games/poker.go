package games

import (
	"database/sql"
	"fmt"
	"math/rand"
	"net"
	"strconv"
)

func HandlePoker(conn net.Conn, db *sql.DB, usuario string, montoStr string, accion string) {
	monto, err := strconv.ParseFloat(montoStr, 64)
	if err != nil || monto <= 0 {
		conn.Write([]byte("ERROR|Monto invalido"))
		return
	}

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

	win := rand.Intn(2) == 1
	var nuevoSaldo float64
	resultado := "loss"

	if win {
		nuevoSaldo = saldoActual + monto
		resultado = "win"
		db.Exec("UPDATE users SET balance = $1 WHERE username = $2", nuevoSaldo, usuario)
		conn.Write([]byte(fmt.Sprintf("OK|WIN|%.2f|%.2f", monto*2, nuevoSaldo)))
	} else {
		nuevoSaldo = saldoActual - monto
		db.Exec("UPDATE users SET balance = $1 WHERE username = $2", nuevoSaldo, usuario)
		conn.Write([]byte(fmt.Sprintf("OK|LOSE|0|%.2f", nuevoSaldo)))
	}

	db.Exec(`INSERT INTO gamelogs (userid, gametype, betamount, result)
		SELECT id, 'poker', $1, $2 FROM users WHERE username = $3`,
		monto, resultado, usuario)

	fmt.Printf("Poker — %s aposto $%.2f (accion: %s) → %s (saldo: $%.2f)\n",
		usuario, monto, accion, resultado, nuevoSaldo)
}
