#!/usr/bin/env python3

import socket
import time

HOST = '127.0.0.1'      # Localhost
INTERNAL_PORT = 8080   # HTTP proxy internal port
EXTERNAL_PORT = 80    # Port for server connection

""" recv function with no length limit """
def recv_timeout(socket, timeout=3):
    socket.setblocking(0)
    total_data = []
    data = ''

    begin = time.time()
    while True:
        if total_data and time.time() - begin > timeout:
            break

        elif time.time() - begin > timeout * 2:
            break

        try:
            data = socket.recv(8192)
            if data:
                total_data.append(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        except:
            pass
    return b''.join(total_data)


print("Init proxy...")
proxy_running = True

""" We create a local proxy on the port INTERNAL_PORT and we listen, waiting for a request """
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.bind((HOST, INTERNAL_PORT))

while proxy_running:
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

        print("Checking for alteration...")
        if "smiley.jpg" in url:
            url = "http://zebroid.ida.liu.se/fakenews/trolly.jpg"

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
        #server_response = server_socket.recv(4096)
        server_response = recv_timeout(server_socket)
        print("Response from the server.")

        """ Request analysis """
        status_code = server_response[:25].decode("utf-8").split("\n")[0].split(' ')[1]
        if status_code != "200":
            print("The server returned an error, status code: ", status_code)
            print("Error bypass attempt...")

        """ Request alteration """
        print("Server response alteration")
        server_response = server_response.replace(b'Smiley', b'Trolly')
        server_response = server_response.replace(b'Stockholm', b'Linkoping')

        """ We just resend the altered server response to the client """
        print("Transmitting the altered response to the client")
        client_connection.sendall(server_response)

        server_socket.close()

        # DEBUG
        print("")
        print("DEBUG:")
        print(data)
        print(new_request)
        print(server_response)
        print("")
        # END DEBUG

        time.sleep(2)
        """ If this is not a GET request """
    else:
        print("Receiving an unsupported method: ", method)

    if not proxy_running:
        break

client_socket.close()
