import socket
import os
import Heatmap_Generator
import time

PORT = 5556
SEPARATOR = "<SEPERATOR>"
BUFFER_SIZE = 4096
MESSAGE_SIZE = 1024

def pad_string(text, length=MESSAGE_SIZE, char=' '):
    return text.ljust(length, char)

def send_file(socket, fileToSend):
    fileSize = os.path.getsize(fileToSend)
    message = fileToSend + SEPARATOR + str(fileSize)
    message = pad_string(message)
    socket.send(message.encode())

    with open(fileToSend, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in busy networks
            socket.sendall(bytes_read)

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print("I'm the server. Socket created.")

s.bind(('', PORT))
print("Socket bound to %s" %(PORT))

s.listen(5)
print("Socket listening")

while True:
    client_socket, addr = s.accept()
    try:
        received = client_socket.recv(MESSAGE_SIZE).decode()
        requestedInputFilename, requestColorString = received.split(SEPARATOR)
        requestColorString = requestColorString.strip()

        print(f"Trying to make a heatmap for {requestedInputFilename}")

        if os.path.exists(requestedInputFilename):
            result = Heatmap_Generator.handle_request(requestedInputFilename, "Output.png", requestColorString)
            if result[0]:
                client_socket.send(pad_string('00 Created heatmap.').encode())
                send_file(client_socket, "Output.png")
            else:
                reply = '02 Could not create heatmap: Error: ' + result[1]
                client_socket.send(pad_string(reply).encode())

            # Delete local files
            os.remove(requestedInputFilename)
            os.remove("Output.png")
        else:
            client_socket.send(pad_string('01 I do not have this file.').encode())

    finally:
        client_socket.close()

s.close()