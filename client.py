# creates localhost UDP socket for communication with server on localhost and provided valid port from command line argument.
# constantly receives messages broadcasted by server (including what other clients sent) and constantly takes input to messages to server 
# author: Sean Zhang (szhang6@umbc.edu, grs.sean.zhang@gmail.com)

import os
import sys
import socket
import threading

# constantly receives and prints broadcasts from server (which is all the clients' messages and server's messages).
def receivingServerMessages():
    while True:
        try:
            message = client.recvfrom(1024)[0]
            print(message.decode())
        except ConnectionResetError:   
            print("The server has been closed. Exiting.")
            os._exit(1)
        except OSError:   # stop receiving when client socket is closed.
            break

# constantly sends message to server in the format "[NAME].[ID],[ACTUAL MESSAGE]". Server uses period and comma as delimiters.
def sendingClientMessages():
    while True:
        clientInput = input()
        clientMessage = name + "." + clientID + "," + clientInput
        # closes client socket when user inputs "!EXIT".
        if clientMessage[clientMessage.index(",") + 1:] == "!EXIT":
            client.sendto(clientMessage.encode(), (HOST, port))
            print("You have left the server. Goodbye.")
            client.close()
            break
        else:
            client.sendto(clientMessage.encode(), (HOST, port))

#create client UDP socket on localhost and available port.
HOST = "127.0.0.1"
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind((HOST, 0))
clientID = str(client.getsockname()[1])   # client ID is their port #.

while True:
    try:
        # checking if user supplied command line with valid UDP port.
        port = int(sys.argv[1])
        if port < 1025 or port > 65535:
            print("The supplied argument for the UDP port must be between 1025 and 65535 inclusive.")
            break
        # takes user name input and sends to server with leading "NewUser:" to inform it is a new client. 
        # No period or comma because they are used as delimiters for message name and ID.
        while True:
            name = input("What will be your display name? Cannot contain periods or commas. ")
            if "." in name or "," in name:
                print("Contains periods or commas.")
                continue
            else:
                break
        client.sendto(("NewUser:" + name).encode(), (HOST, port))
        message = client.recvfrom(1024)[0]   #receives it's welcome broadcast from server. Throws ConnectionResetError if server not at port inputted
        print(message.decode())
        threading.Thread(target = receivingServerMessages).start()
        threading.Thread(target = sendingClientMessages).start()
        break
    except IndexError:
        print("Please supply an additional argument specifying UDP port number.")
        sys.exit(1)
    except ValueError:
        print("The supplied argument for the UDP port must be an integer.")
        sys.exit(1)
    except ConnectionResetError:
        print("Could not communicate with host port " + str(port) + ". Make sure server is up on that port.")
        sys.exit(1)
        

