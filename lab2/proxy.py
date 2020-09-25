#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    TDTS06 - Computer networks 2020/21
    Mayeul G. & Pierre M.
    Last modification: 2020-09-25
    First release: 2020-09-25 (rev 1)

    Websites to try our very basic proxy:
        http://zebroid.ida.liu.se/fakenews/test2.html
        http://zebroid.ida.liu.se/fakenews/test4.html

    Note to the corrector:
    """ """ comments are used to describe the general operation of a passage 
    while # comments describe the operation of a particular line.
    
    Usage: proxy.py [-h] [--debug] [--settimeoutglobal] [--port PORT]

    Optional arguments:
            -h, --help              show the help message and exit
            --debug                 print debug information
            --settimeoutglobal      do not suppose the client's internet speed. For slow connections.
            --port PORT             set the port to use for the client side connection

"""


import argparse     # For program's argument management
import re           # To find patterns
import signal       # To implement a signal handler
import socket       # A low level socket programming library
import time         # To manage timeout
import _thread      # Library for multi-threading


""" Proxy general parameters (default values) """
HOST = '127.0.0.1'      # Localhost
INTERNAL_PORT = 8080   # HTTP proxy internal port (can be change by user using --port PORT)
EXTERNAL_PORT = 80   # Port for server connection

""" Alteration parameters """
REPLACE1 = "Trolly"
REPLACE2 = "Linköping"
PATTERN1 = re.compile("Smiley", re.IGNORECASE)
PATTERN2 = re.compile("Stockholm", re.IGNORECASE)

""" Dev. parameters """
DEBUG = False               # Can be change by passing --debug arg
SUPPOSE_INTERNET = True     # Can be change by passing --settimeoutglobal arg


""" recv function with no length limit """
def recv_timeout(socket, packet_timeout=0.5, global_timeout=3):
    # Reset timeout
    timeout = packet_timeout
    socket.setblocking(0)
    first_pkt = True
    # Variables containing our data
    total_data = []

    begin = time.time()
    global_begin = time.time()
    while True:
        # Check for packet timeout
        if total_data and time.time() - begin > timeout:
            break

        # Check for global timeout
        if total_data and time.time() - global_begin > global_timeout:
            break

        elif time.time() - begin > timeout * 2 or time.time() - global_begin > global_timeout:
            break

        # Try to receive data
        try:
            data = socket.recv(8192)

            # Trying to find the Content_Length field
            if first_pkt and SUPPOSE_INTERNET:
                first_pkt = False
                try:
                    pos = data.find(b'Content-Length:')
                    pos_end = data.find(b'\r', pos, len(data) - 1)
                    if DEBUG:
                        print("DEBUG: Find 'Content_length' field:")
                        print(data[pos+16:pos_end])
                    content_length = data[pos+16:pos_end]

                    """ Here, we try to estimate a correct timeout by assuming the client's internet speed. 
                    We cannot estimate this flow ourselves because it is much too long as a procedure."""
                    # Supposing a minimum 100 KBytes/sec
                    global_timeout = content_length * 0.00001
                except:
                    pass

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
    tmp = ""
    analyse_start = 0
    r_end = len(altered_request) - 1
    # Searching for image
    img_pos = altered_request.find('<img src="', analyse_start, r_end)
    while img_pos > -1:
        # We alter until the start of <img ...>
        final_request += PATTERN2.sub(REPLACE2, PATTERN1.sub(REPLACE1, altered_request[analyse_start:img_pos]))

        analyse_start = altered_request.find('">', img_pos, r_end)
        # We do not modify the inside of <img ...>
        final_request += altered_request[img_pos:analyse_start]
        # We search for another image
        img_pos = altered_request.find('<img src=', analyse_start, r_end)

    # We alter the end of the request
    final_request += PATTERN2.sub(REPLACE2, PATTERN1.sub(REPLACE1, altered_request[analyse_start:img_pos]))
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


def send_server(t_url, t_protocol, t_server, t_client_connection):
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
    t_client_connection.sendall(server_response)
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


""" Code entry """
""" We check for arguments """
parser = argparse.ArgumentParser(description='A very basic HTTP proxy.')
parser.add_argument('--debug', help='print debug information', action='store_true')
parser.add_argument('--settimeoutglobal', help='po not suppose the client\'s internet speed. For slow connection.', action='store_true')
parser.add_argument('--port', help='set the port to use for the client side connection')
args = parser.parse_args()
if args.debug:
    DEBUG = True
if args.port:
    INTERNAL_PORT = int(args.port)
if args.settimeoutglobal:
    SUPPOSE_INTERNET = False


""" Starting proxy initialisation """
print("Init proxy...")
# Launching signal handler
signal.signal(signal.SIGINT, signal_handler)


""" We create a local proxy on the port INTERNAL_PORT and we listen, waiting for a request """
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.bind((HOST, INTERNAL_PORT))
request_count = 0


while True:
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

        _thread.start_new_thread(send_server, (url, protocol, server, client_connection))
        request_count += 1

        """ If this is not a GET request """
    else:
        print("Receiving an unsupported method: ", method)
        if DEBUG:
            print("")
            print("DEBUG:")
            print(data)
            print("")
