import socket
import json
from strToHex import color_name_to_hex

HOST = 'localhost'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    print(f"strToHex server listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            data = conn.recv(1024).decode('utf-8')
            if not data:
                continue

            try:
                request = json.loads(data)
                color_name = request.get('color_name')
                hex_code = color_name_to_hex(color_name)

                response = {'hex_code': hex_code} if hex_code else {'error': 'Invalid color name'}
                print(f"Sending back: {response}")
                conn.sendall(json.dumps(response).encode('utf-8'))

            except Exception as e:
                print(f"Server error: {e}")
                conn.sendall(json.dumps({'error': 'Server error'}).encode('utf-8'))