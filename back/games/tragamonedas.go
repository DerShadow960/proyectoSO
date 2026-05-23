package games

import (
	"database/sql"
	"fmt"
	"math/rand"
	"net"
	"strconv"
)

func HandleTragamonedas(conn net.Conn, db *sql.DB, usuario string, montoStr string) {
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

	r1 := rand.Intn(10)
	r2 := rand.Intn(10)
	r3 := rand.Intn(10)
	win := r1 == r2 && r2 == r3

	var nuevoSaldo float64
	resultado := "loss"
	if win {
		nuevoSaldo = saldoActual + (monto * 10)
		resultado = "win"
		db.Exec("UPDATE users SET balance = $1 WHERE username = $2", nuevoSaldo, usuario)
		conn.Write([]byte(fmt.Sprintf("OK|WIN|%.2f|%d|%d|%d|%.2f", monto*10, r1, r2, r3, nuevoSaldo)))
	} else {
		nuevoSaldo = saldoActual - monto
		db.Exec("UPDATE users SET balance = $1 WHERE username = $2", nuevoSaldo, usuario)
		conn.Write([]byte(fmt.Sprintf("OK|LOSE|0|%d|%d|%d|%.2f", r1, r2, r3, nuevoSaldo)))
	}

	db.Exec(`INSERT INTO gamelogs (userid, gametype, betamount, result)
		SELECT id, 'tragamonedas', $1, $2 FROM users WHERE username = $3`,
		monto, resultado, usuario)

	fmt.Printf("Tragamonedas — %s aposto $%.2f → [%d|%d|%d] → %s (saldo: $%.2f)\n",
		usuario, monto, r1, r2, r3, resultado, nuevoSaldo)
}
