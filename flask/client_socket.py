import socket
import os

HOST = '127.0.0.1'
UPLOAD_PORT = 5555
REQUEST_PORT = 5556
SEPARATOR = "<SEPERATOR>"
BUFFER_SIZE = 4096
MESSAGE_SIZE = 1024

def pad_string(text, length=MESSAGE_SIZE, char=' '):
    return text.ljust(length, char)

def upload_csv(file_path):
    s = socket.socket()
    print(f"Attempting to connect to {HOST}:{UPLOAD_PORT}")
    s.connect((HOST, UPLOAD_PORT))
    
    file_size = os.path.getsize(file_path)
    message = f"{os.path.basename(file_path)}{SEPARATOR}{file_size}"
    s.send(pad_string(message).encode())

    with open(file_path, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            s.sendall(bytes_read)
    s.close()

def request_heatmap(file_name, color_string=""):
    s = socket.socket()
    print(f"Attempting to connect to {HOST}:{REQUEST_PORT}")
    s.connect((HOST, REQUEST_PORT))

    message = f"{file_name}{SEPARATOR}{color_string}"
    s.send(pad_string(message).encode())

    # Receive status reply (1024 bytes)
    reply = s.recv(MESSAGE_SIZE).decode().strip()
    if not reply.startswith("00"):
        s.close()
        raise Exception(f"Heatmap request failed: {reply[3:]}")
    
    # Receive image file info
    received = s.recv(MESSAGE_SIZE).decode()
    _, filesize = received.split(SEPARATOR)
    filesize = int(filesize)

    # Receive image data
    image_data = b""
    while len(image_data) < filesize:
        chunk = s.recv(BUFFER_SIZE)
        if not chunk:
            break
        image_data += chunk
    
    s.close()
    return image_data