import socket
import os

# HOST = 'localhost'
HOST = '3.131.47.90'
UPLOAD_PORT = 5555
REQUEST_PORT = 5556
SEPARATOR = "<SEPERATOR>"
BUFFER_SIZE = 4096
MESSAGE_SIZE = 1024

def pad_string(text, length=MESSAGE_SIZE, char=' '):
    return text.ljust(length, char)

def initUploadSocket():
    s = socket.socket()
    s.connect((HOST, UPLOAD_PORT))
    print(f"Connected to file upload socket at {HOST}:{UPLOAD_PORT}")
    return s

def uploadFile(socket, requestFileName):
    fileSize = os.path.getsize(requestFileName)
    message = requestFileName + SEPARATOR + str(fileSize)
    print('I sent a message to the file upload server: ' + message)
    message = pad_string(message)
    socket.send(message.encode())

    print('I sent a file to the file upload server: ' + requestFileName)
    with open(requestFileName, "rb") as f:
        while True:
            # read 4kB bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            socket.sendall(bytes_read)

def initRequestSocket():
    s = socket.socket()
    s.connect((HOST, REQUEST_PORT))
    print(f"Connected to request socket at {HOST}:{REQUEST_PORT}")
    return s

def requestHeatmap(socket, requestFileName, colorString):
    message = requestFileName + SEPARATOR + colorString
    print('I sent a message to the request server: ' + message)
    message = pad_string(message)
    socket.send(message.encode())

def isReplySuccessful(socket):
    reply = socket.recv(MESSAGE_SIZE).decode().strip()
    print('I received a message from the request server: ' + reply)
    if reply[:2] != '00':
        return False
    else:
        return True

def receiveFile(socket, newFilename):
    received = socket.recv(MESSAGE_SIZE).decode().strip()
    print('I received a message from the request server: ' + received)
    filename, filesize = received.split(SEPARATOR)

    with open(newFilename, "wb") as f:
        while True:
            # read 4kB from the socket (receive)
            bytes_read = socket.recv(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)

    print('I received a file from the request server and wrote it to: ' + newFilename)
    return

def getHeatmap(dataFile, imageFileName, colorString):
    uploadSocket = initUploadSocket()
    uploadFile(uploadSocket, dataFile)
    uploadSocket.close()

    requestSocket = initRequestSocket()
    requestHeatmap(requestSocket, dataFile, colorString)
    if isReplySuccessful(requestSocket):
        receiveFile(requestSocket,imageFileName)
    requestSocket.close()

if __name__ == "__main__":
    getHeatmap("ExampleData01.csv", "ReturnedImage01.png", "#DD00DD #EE88EE #FFFFFF")
    # getHeatmap("ExampleData03.csv", "ReturnedImage03.png", '')