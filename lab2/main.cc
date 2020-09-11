/*
TDTS06 - Computer networks - Lab 2
Mayeul G. & Pierre M.
Last modified: 2020-09-11²
*/

#include <iostream>
#include <sys/socket.h>
#include <string.h>
#include <netdb.h> 


#define PORT 8080

using namespace std;

void print(string str){
    cout << str << flush;
}

int main() {
    print("Starting proxy server...\n");

    print("Trying to create socket...");
    int our_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (our_socket < 0) {print("Fail!\nExiting..."); exit(1);}
    print("OK!\n");
    
    struct sockaddr_in server_address, client_address;
    
    return 0;
}