package main

import (
	"fmt"
	"net"
	"os"
	"time"
)

func main() {
	host := "localhost"
	if len(os.Args) > 1 {
		host = os.Args[1]
	}

	ports := []string{"12010", "54321", "5432"}
	fmt.Printf("Escaneando %s: \n", host)
	tcpGather(host, ports)
}

func tcpGather(host string, ports []string) map[string]string {
	results := make(map[string]string)
	for _, port := range ports {
		address := net.JoinHostPort(host, port)
		conn, err := net.DialTimeout("tcp", address, 3*time.Second)

		if err != nil {
			results[port] = "failed"
		} else {
			results[port] = "success"
			_ = conn.Close()
		}
	}

	for port, status := range results {
		if status == "success" {
			fmt.Printf("Puerto %s: ENABLED \n", port)
		}
	}

	return results
}
