#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    TDTS06 - Computer networks 2020/21
    Mayeul G. & Pierre M.
    Last modification: 2020-09-20

    Websites to try our very basic proxy:
        http://zebroid.ida.liu.se/fakenews/test2.html
        http://zebroid.ida.liu.se/fakenews/test4.html

    Note to the corrector:
    """ """ comments are used to describe the general operation of a passage 
    while # comments describe the operation of a particular line.
"""


import socket
import signal
import time
import _thread


""" Proxy general parameters """
HOST = '127.0.0.1'      # Localhost
INTERNAL_PORT = 8080   # HTTP proxy internal port
EXTERNAL_PORT = 80   # Port for server connection

""" Alteration parameters """
SEARCH1 = "Smiley"
REPLACE1 = "Trolly"
SEARCH2 = "Stockholm"
REPLACE2 = "Linköping"

""" Dev. parameters """
DEBUG = True


""" recv function with no length limit """
def recv_timeout(socket, timeout=3):
    # Reset timeout
    socket.setblocking(0)
    # Variables containing our data
    total_data = []
    data = ''

    begin = time.time()
    while True:
        # Check for timeout
        if total_data and time.time() - begin > timeout:
            break

        elif time.time() - begin > timeout * 2:
            break

        # Try to receive data
        try:
            data = socket.recv(8192)
            if data:
                total_data.append(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        # Except no data
        except:
            pass
    return b''.join(total_data)


""" 
A function which alter a request
    This function is particularly complex since it is necessary
    to replace words by others while ensuring that these 
    replaced words are not image addresses.
"""
def altered(request):
    try:
        # Decoding the request to analyse it
        altered_request = request.decode("utf-8")
    except UnicodeDecodeError:
        return request

    """ 
    The purpose of this part is to remplace 'Smiley' by 'Trolly'
    and 'Stockholm' by 'Linköping' everywhere except in image names.
    """
    final_request = ""
    analyse_start = 0
    r_end = len(altered_request) - 1
    # Searching for image
    img_pos = altered_request.find('<img src="', analyse_start, r_end)
    while img_pos > -1:
        # We alter until the start of <img ...>
        final_request += altered_request[analyse_start:img_pos].replace(SEARCH1, REPLACE1).replace(SEARCH2, REPLACE2)

        analyse_start = altered_request.find('">', img_pos, r_end)
        # We do not modify the inside of <img ...>
        final_request += altered_request[img_pos:analyse_start]
        # We search for another image
        img_pos = altered_request.find('<img src=', analyse_start, r_end)

    # We alter the end of the request
    final_request += altered_request[analyse_start:img_pos].replace(SEARCH1, REPLACE1).replace(SEARCH2, REPLACE2)
    return bytes(final_request, "utf-8")


""" A basic SIGINT handler"""
def signal_handler(sig, frame):
    print('Stopping...')
    try:
        # Try closing client socket
        client_socket.close()
    except NameError:
        pass
    try:
        # Try closing server socket
        server_socket.close()
    except NameError:
        pass

    exit(0)


def send_server(t_url, t_protocol, t_server):
    """ Attempt to resend the request to the server """
    print("Trying to reach the website:")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    t_server_ip = socket.gethostbyname(t_server)
    server_socket.connect((t_server_ip, EXTERNAL_PORT))
    print("Connected to server...")
    print("Sending request...")
    new_request = bytes("GET " + t_url + " " + t_protocol + "\nHost: " + t_server + "\r\n\r\n", "utf-8")
    server_socket.sendall(new_request)

    """ Waiting fo response """
    print("Request sent.")
    server_response = recv_timeout(server_socket)
    print("Response from the server.")

    """ Request analysis """
    status_code = server_response[:25].decode("utf-8").split("\n")[0].split(' ')[1]
    if status_code != "200":
        print("The server returned an error, status code: ", status_code)
        print("Error bypass attempt...")

    """ Text alteration """
    print("Server response alteration")
    server_response = altered(server_response)

    """ We just resend the altered server response to the client """
    print("Transmitting the altered response to the client")
    client_connection.sendall(server_response)
    server_socket.close()

    # DEBUG
    if DEBUG:
        print("")
        print("DEBUG:")
        print(data)
        print(new_request)
        print(server_response)
        print("")
    # END DEBUG



print("Init proxy...")
proxy_running = True
# Launching signal handler
signal.signal(signal.SIGINT, signal_handler)
request_count = 0


""" We create a local proxy on the port INTERNAL_PORT and we listen, waiting for a request """
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

    if "detectportal.firefox.com/success.txt" in request:
        pass
    elif method == "GET":
        """ If it is a GET request, we extract any useful information """
        url = header[1]
        server = url.split('/')[2]
        server_ip = socket.gethostbyname(server)
        protocol = header[2]
        print("Interception of a GET method requesting the URL: ", url)
        print("Destination server: ", server, " (", server_ip, ")")

        """ Image alteration """
        print("Checking for alteration...")
        if "smiley.jpg" in url:
            url = "http://zebroid.ida.liu.se/fakenews/trolly.jpg"


        _thread.start_new_thread(send_server, (url, protocol, server))
        request_count += 1
        time.sleep(2)

        """ If this is not a GET request """
    else:
        print("Receiving an unsupported method: ", method)
        if DEBUG:
            print("")
            print("DEBUG:")
            print(data)
            print("")

    if not proxy_running:
        break

client_socket.close()
