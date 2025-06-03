import socket

HOST = '127.0.0.1'  # can replace later (i.e. 'example.aws.com')
PORT = 65432

def send_color_name(color_name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(color_name.encode())
        data = s.recv(1024).decode()
        return data

if __name__ == '__main__':
    color = input("Enter a color name: ").strip()
    hex_code = send_color_name(color)
    print(f"Hex code: {hex_code}")