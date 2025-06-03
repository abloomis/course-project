import socket
import os

# Set the HOST to your peer's remote IP address
HOST = '3.131.47.90'
UPLOAD_PORT = 5555
REQUEST_PORT = 5556
SEPARATOR = "<SEPERATOR>"
BUFFER_SIZE = 4096
MESSAGE_SIZE = 1024

def pad_string(text, length=MESSAGE_SIZE, char=' '):
    return text.ljust(length, char)

def upload_csv(file_path):
    """
    Connects to the remote upload server and sends a CSV file.
    file_path: The local path to the CSV file to be uploaded.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Specify IPv4 and TCP
    print(f"Attempting to connect to {HOST}:{UPLOAD_PORT} for CSV upload...")
    try:
        s.connect((HOST, UPLOAD_PORT))
        
        file_size = os.path.getsize(file_path)
        # Send only the basename of the file, as the remote server expects this
        message = f"{os.path.basename(file_path)}{SEPARATOR}{file_size}"
        s.send(pad_string(message).encode())

        with open(file_path, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break # File transmitting is done
                s.sendall(bytes_read)
        print(f"Successfully uploaded {os.path.basename(file_path)} to {HOST}:{UPLOAD_PORT}")
    except socket.error as e:
        raise ConnectionError(f"Could not connect or send file to remote heatmap upload server: {e}")
    finally:
        s.close()

def request_heatmap(file_name, color_string=""):
    """
    Connects to the remote request server, requests a heatmap, and receives the image data.
    file_name: The basename of the CSV file already uploaded to the remote server.
    color_string: The color string for the heatmap (e.g., "#00FF00 #FFFF00 #FF0000").
    Returns: Binary image data (bytes).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Specify IPv4 and TCP
    print(f"Attempting to connect to {HOST}:{REQUEST_PORT} for heatmap request...")
    try:
        s.connect((HOST, REQUEST_PORT))

        message = f"{file_name}{SEPARATOR}{color_string}"
        s.send(pad_string(message).encode())

        # Receive status reply (1024 bytes)
        reply = s.recv(MESSAGE_SIZE).decode().strip()
        if not reply.startswith("00"):
            raise Exception(f"Heatmap request failed on remote server: {reply[3:]}")
        
        # Receive image file info
        received_metadata = s.recv(MESSAGE_SIZE).decode().strip()
        filename_received, filesize_str = received_metadata.split(SEPARATOR)
        filesize = int(filesize_str)
        print(f"Receiving image: {filename_received}, size: {filesize} bytes")

        # Receive image data
        image_data = b""
        total_bytes_received = 0
        while total_bytes_received < filesize:
            chunk = s.recv(BUFFER_SIZE)
            if not chunk:
                # Connection closed prematurely
                break
            image_data += chunk
            total_bytes_received += len(chunk)
        
        if total_bytes_received != filesize:
            print(f"Warning: Expected {filesize} bytes but received {total_bytes_received} bytes.")

        print(f"Successfully received heatmap image data from {HOST}:{REQUEST_PORT}")
        return image_data
    except socket.error as e:
        raise ConnectionError(f"Could not connect or receive heatmap from remote generator server: {e}")
    finally:
        s.close()

# No `if __name__ == "__main__":` block needed here, as it's meant to be imported.