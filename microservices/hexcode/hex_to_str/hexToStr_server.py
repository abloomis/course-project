import socket
import json
from hexToStr import find_closest_color

def start_server():
    host = 'localhost'
    port = 65433  # Use a different port from strToHex

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"[hexToStr server] Listening on {host}:{port}...")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"[hexToStr] Connected by {addr}")
                data = conn.recv(1024).decode('utf-8')

                try:
                    payload = json.loads(data)
                    hex_code = payload['hex']
                    bin_count = int(payload['bins'])

                    color_name = find_closest_color(hex_code, bin_count)
                    response = {'color_name': color_name}
                except Exception as e:
                    response = {'error': str(e)}

                conn.sendall(json.dumps(response).encode('utf-8'))

if __name__ == '__main__':
    start_server()
