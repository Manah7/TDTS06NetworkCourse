#!/usr/bin/env python3

import socket

HOST = '127.0.0.1'      # Localhost
INTERNAL_PORT = 8080   # HTTP proxy internal port
EXTERNAL_PORT = 80    # Port for server connection

print("Init proxy...")
proxy_running = True

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while proxy_running:
    """ We create a local proxy on the port INTERNAL_PORT and we listen, waiting for a request """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind((HOST, INTERNAL_PORT))
    client_socket.listen()
    print("Proxy ready and waiting...")

    """ We accept any connection on the port and we keep the data sent """
    client_connection, addr = client_socket.accept()
    print("Connected by", addr)
    print("Receiving data...")
    data = client_connection.recv(1024)

    """ Analysis of the request and identification """
    request = data.decode("utf-8").split("\n")
    header = request[0].split(' ')
    method = header[0]

    """ If it is a GET request """
    if method == "GET":
        """ We extract any useful information """
        url = header[1]
        server = url.split('/')[2]
        server_ip = socket.gethostbyname(server)
        protocol = header[2]
        print("Interception of a GET method requesting the URL: ", url)
        print("Destination server: ", server, " (", server_ip, ")")

        """ Attempt to resend the request to the server """
        print("Trying to reach the website:")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((server_ip, EXTERNAL_PORT))
        print("Connected to server...")
        print("Sending request...")
        new_request = bytes("GET " + url + " " + protocol + "\nHost: " + server + "\r\n\r\n", "utf-8")
        server_socket.sendall(new_request)

        """ Waiting fo response """
        print("Request sent.")
        server_response = server_socket.recv(4096)
        print("Response from the server.")

        """ Request analysis """
        status_code = server_response.decode("utf-8").split("\n")[0].split(' ')[1]
        if status_code != "200":
            print("The server returned an error, status code: ", status_code)
            print("Exiting...")
            client_socket.close()
            server_socket.close()

        """ Request alteration """
        print("Server response alteration")
        server_response = server_response.replace(b'Smiley', b'Trolly')
        server_response = server_response.replace(b'Stockholm', b'Linkoping')

        """ We just resend the altered server response to the client """
        print("Transmitting the altered response to the client")
        client_connection.sendall(server_response)
        print("")

        ### DEBUG
        print("DEBUG:")
        print(data)
        print(new_request)
        print(server_response)
        ### END

    # Ending
        server_socket.close()
    client_socket.close()
    break