import socket
import json
import re

HEX_TO_STR_PORT = 65433
STR_TO_HEX_PORT = 65432
HOST = 'localhost'

# helper function using fullmatch to check hex ranges (i.e. no letters past 'F')
def is_valid_hex_color(s):
    # return True if s is a valid hex color string (with or without leading #)
    return bool(re.fullmatch(r'#?[0-9A-Fa-f]{6}', s))

def send_request(payload, port):
    # send a JSON-encoded payload to the server listening on the given port and return the decoded JSON response
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, port))
            s.sendall(json.dumps(payload).encode('utf-8'))
            response = s.recv(1024).decode('utf-8')
            return json.loads(response)
    except ConnectionRefusedError:
        return {'error': f'Could not connect to server on port {port}'}
    except json.JSONDecodeError:
        return {'error': 'Received invalid JSON response'}

# send the request to the appropriate port after parsing the inputs
def convert_color(input_value, bins=None):
    # if input_value is a hex code, bins must be provided, then returns closest color name
    # else, treat input_value as a color name string, then return a hex code
    if is_valid_hex_color(input_value):
        if not input_value.startswith('#'):
            input_value = '#' + input_value
        if bins is None:
            return {'error': 'A color-bin count is required for hex-to-string conversion'}
        payload = {'hex': input_value, 'bins': bins}
        return send_request(payload, HEX_TO_STR_PORT)
    else:
        payload = {'color_name': input_value}
        return send_request(payload, STR_TO_HEX_PORT)