import socket
import os

PORT = 5555
SEPARATOR = "<SEPERATOR>"
BUFFER_SIZE = 4096
MESSAGE_SIZE = 1024

def receiveFile(socket):
    received = socket.recv(MESSAGE_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)

    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)

    with open(filename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print("I'm the server. Socket created.")

s.bind(('', PORT))
print("Socket bound to %s" %(PORT))

s.listen(5)
print("Socket listening")

while True:
    client_socket, addr = s.accept()
    print("Got connection from: ", addr)

    receiveFile(client_socket)

    # close the client socket
    client_socket.close()

# close the server socket
s.close()