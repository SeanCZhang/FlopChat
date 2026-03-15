# creates UDP server with one socket on localhost and provided valid port from command line arguement. Supports multiple clients
# constantly receives client messages sent to server address and broadcasts to all clients. Server also can broadcast messages.
# logs all server and client messages into text file.
# author: Sean Zhang (szhang6@umbc.edu, grs.sean.zhang@gmail.com)

import os
import sys
import socket
import threading
import queue
import datetime

def writeHistory(message):
    with open('ChatHistory.txt', 'a') as file:
        file.write(message + "\n")

def getDate():
    messageDate = datetime.datetime.now()
    return str(messageDate.strftime("%m/%d/%Y %H:%M:%S"))

# constantly receives message and it's address and puts it in messagesandAddresses queue.
def receivingClientMessages():
    while True:
        try:
            message, address = server.recvfrom(1024)
            messagesandAddresses.put((message, address))
        # even though this is UDP, a protocol that does not have connections, the program will return this error if a client program is 
        # closed not using the intended "!EXIT" call (e.g. killing terminal). 
        except ConnectionResetError:
            print("A client connection has been forcibly closed in an unintended way. Closing server.")
            os._exit(1)
        # returns this when socket is closed when server enters '!EXIT'.
        except OSError:
            break

# constantly takes messages from queue and broadcasts to all clients.
def broadcastingClientMessages():
    while True:
        # breaks when thread receivingClientMessages breaks,
        if not t1.is_alive():
            break
        while not messagesandAddresses.empty():
            currentMessageandAddress = messagesandAddresses.get()
            currentMessage = currentMessageandAddress[0].decode()
            currentMessageAddress = currentMessageandAddress[1]    # is tuple: ([IP ADDRESS], [PORT])
            # all new clients' first message start with "NewUser:" followed by their name. Broadcasts welcome message with their name and ID (Their port #).
            if currentMessage.startswith("NewUser:") and currentMessageAddress not in currentClientAddresses:
                name = currentMessage[currentMessage.index(":") + 1:]
                welcomeMsg = ("[" + getDate() + "] ANNOUNCEMENT: " + name + " (ID: " + str(currentMessageAddress[1]) + ") has joined, welcome. Enter '!EXIT' to leave the server.")
                currentClientAddresses.append(currentMessageAddress)
                for clientAddress in currentClientAddresses:
                    server.sendto((welcomeMsg).encode(), clientAddress)
                print(welcomeMsg)
                writeHistory(welcomeMsg)
            # all messages after the first from each client are in the format "[NAME].[ID],[ACTUAL MESSAGE]". Period and Comma used to delimit sections.
            else:
                messageName = currentMessage[:currentMessage.index(".")]
                messageID = currentMessage[currentMessage.index(".")+1:currentMessage.index(",")]
                messagePayload = currentMessage[currentMessage.index(",") + 1:]     # the actual message client sent.
                # broadcast when client leaves server when they input "!EXIT".
                if messagePayload == "!EXIT":
                    currentClientAddresses.remove(currentMessageAddress)
                    leaveMsg = ("[" + getDate() + "] ANNOUNCEMENT: " + messageName + " (ID:" + messageID + ") has left the server.")
                    for clientAddress in currentClientAddresses:
                        server.sendto(leaveMsg.encode(), clientAddress)
                    print(leaveMsg)
                    writeHistory(leaveMsg)
                # broadcast client message.
                else:
                    clientMsg = ("[" + getDate() + "] " + messageName + " (ID:" + messageID + "): " + messagePayload)
                    for clientAddress in currentClientAddresses:
                        server.sendto(clientMsg.encode(), clientAddress)
                    print(clientMsg)
                    writeHistory(clientMsg)

# constantly takes input and broadcasts to all clients. Closes server if input "!EXIT".
def sendingServerMessages():
    while True:
        serverInput = input()
        if serverInput == "!EXIT":
            print("Server has been closed. Goodbye Pork Pie Hat.")
            server.close()
            break
        else:
            serverMsg = ("[" + getDate() + "] Server: " + serverInput)
            for clientAddress in currentClientAddresses:
                server.sendto(serverMsg.encode(), clientAddress)
            print(serverMsg)
            writeHistory(serverMsg)

currentClientAddresses = []
messagesandAddresses = queue.Queue() # messages from clients are put and gotten here.

# checking if user supplied command line with valid UDP port.
try:
    port = int(sys.argv[1])
    if port < 1025 or port > 65535:
        print("The supplied argument for the UDP port must be between 1025 and 65535 inclusive.")
        sys.exit(1)
except IndexError:
    print("Please supply an additional argument specifying UDP port number.")
    sys.exit(1)
except ValueError:
    print("The supplied argument for the UDP port must be an integer.")
    sys.exit(1)

# create UDP server socket on localhost with provided port .
HOST = "127.0.0.1"
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, port))
print("UDP server up on port " + str(port) +". Enter '!EXIT' to close server.")
writeHistory("\n|||UDP server created on [" + getDate() + "] on port " + str(port) + "|||\n")

t1 = threading.Thread(target = receivingClientMessages)
t2 = threading.Thread(target = broadcastingClientMessages)
t3 = threading.Thread(target = sendingServerMessages)
t1.start()
t2.start()
t3.start()

