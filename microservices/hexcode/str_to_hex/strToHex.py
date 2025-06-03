import sys
from colorLibrary import color_name_to_hex

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: strToHex.py <color_name>")
    else:
        color_name = sys.argv[1]
        hex_result = color_name_to_hex(color_name)
        if hex_result:
            print(hex_result)
        else:
            print("Color not found")