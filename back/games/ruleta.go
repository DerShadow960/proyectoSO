package games

import (
	"database/sql"
	"fmt"
	"math/rand"
	"net"
	"strconv"
)

var NumerosRojos = map[int]bool{
	1: true, 3: true, 5: true, 7: true, 9: true, 12: true, 14: true,
	16: true, 18: true, 19: true, 21: true, 23: true, 25: true, 27: true,
	30: true, 32: true, 34: true, 36: true,
}

func HandleRuleta(conn net.Conn, db *sql.DB, usuario string, montoStr string, opcion string) {
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

	spin := rand.Intn(38)
	win := false
	payout := 0.0
	spinStr := strconv.Itoa(spin)
	if spin == 37 {
		spinStr = "00"
	}

	switch opcion {
	case "rojo":
		win = NumerosRojos[spin]
		payout = monto * 2
	case "negro":
		win = spin > 0 && spin != 37 && !NumerosRojos[spin]
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
		if opcion == spinStr {
			win = true
			payout = monto * 36
		}
	}

	var nuevoSaldo float64
	if win {
		nuevoSaldo = saldoActual - monto + payout
	} else {
		nuevoSaldo = saldoActual - monto
	}

	_, err = db.Exec("UPDATE users SET balance = $1 WHERE username = $2", nuevoSaldo, usuario)
	if err != nil {
		conn.Write([]byte("ERROR|No se pudo actualizar saldo"))
		return
	}

	resultado := "loss"
	if win {
		resultado = "win"
	}
	db.Exec(`INSERT INTO gamelogs (userid, gametype, betamount, result)
		SELECT id, 'ruleta', $1, $2 FROM users WHERE username = $3`,
		monto, resultado, usuario)

	fmt.Printf("Ruleta — %s aposto $%.2f a '%s' → numero %s → %s (saldo: $%.2f)\n",
		usuario, monto, opcion, spinStr, resultado, nuevoSaldo)

	if win {
		conn.Write([]byte(fmt.Sprintf("OK|WIN|%.2f|%s|%.2f", payout, spinStr, nuevoSaldo)))
	} else {
		conn.Write([]byte(fmt.Sprintf("OK|LOSE|0|%s|%.2f", spinStr, nuevoSaldo)))
	}
}
