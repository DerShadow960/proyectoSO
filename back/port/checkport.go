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
	//raw_connect(host, ports)
	tcpGather(host, ports)
}

//func raw_connect(host string, ports []string) {
//	for _, port := range ports {
//		timeout := 1 * time.Second
//		conn, err := net.DialTimeout("tcp", net.JoinHostPort(host, port), timeout)
//
//		if err != nil {
//			fmt.Printf("Puerto %s: CERRADO \n", port)
//			continue
//		}
//
//		fmt.Printf("Puerto %s: ABIERTO  \n", port)
//		conn.Close()
//	}
//}

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
	fmt.Printf("%s\n", results)
	return results
}
