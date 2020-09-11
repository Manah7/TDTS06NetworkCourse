#!/usr/bin/env python3

import socket
import requests

HOST = '127.0.0.1'      # Localhost
INTERNAL_PORT = 8080    # HTTP proxy internal port
EXTERNAL_PORT = 8081    # Port for server connection

print("Init proxy...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.bind((HOST, INTERNAL_PORT))
    client_socket.listen()
    print("Proxy ready and waiting...")

    conn, addr = client_socket.accept()
    with conn:
        print("Connected by", addr)
        print("Receiving data...")
        data = conn.recv(1024)
        print(data.decode("utf-8"))

        request = data.decode("utf-8").split("\n")
        header = request[0].split(' ')
        method = header[0]

        if method == "GET":
            url = header[1]
            server = url.split('/')[2]
            server_ip = socket.gethostbyname(server)
            protocol = header[2]
            print("Interception of a GET method requesting the URL: ", url)
            print("Destination server: ", server, " (", server_ip, ")")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, EXTERNAL_PORT))

    server_socket.connect((server_ip, 80))
    sent = server_socket.send(bytes(request[0], "utf-8"))

    server_socket.listen()
    conn, addr = server_socket.accept()
    with conn:
        print("Connected by", addr)
        print("Receiving data...")
        data = conn.recv(1024)
        print(data.decode("utf-8"))

    pass
