#!/usr/bin/env python3

import socket

HOST = '127.0.0.1'      # Localhost
INTERNAL_PORT = 8080   # HTTP proxy internal port
EXTERNAL_PORT = 80    # Port for server connection

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

    print("Trying to reach the website:")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((server_ip, EXTERNAL_PORT))
    print("Connected to server...")
    print("Sending request...")
    sent = server_socket.sendall(bytes(request[0], "utf-8"))
    print("Request sent.")
    print(server_socket.recv(4096))
    pass
