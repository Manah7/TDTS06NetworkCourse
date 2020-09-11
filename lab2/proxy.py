#!/usr/bin/env python3

import socket

HOST = '127.0.0.1'  # Localhost
PORT = 8080         # HTTP proxy port

print("Init test.")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    conn, addr = server_socket.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(data)