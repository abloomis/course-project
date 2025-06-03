import sys
from colorBins import COLOR_BINS

def hex_to_rgb(hex_str):
    # remove the pound symbol from the inputted str
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))

# calculate the distance 
def color_distance(c1, c2):
    return sum((a - b) ** 2 for a, b in zip(c1, c2))

def find_closest_color(hex_code, bin_count):
    color_map = COLOR_BINS.get(bin_count)
    if not color_map:
        return 'Invalid bin count'

    input_rgb = hex_to_rgb(hex_code)
    closest = min(color_map.items(), key=lambda kv: color_distance(input_rgb, hex_to_rgb(kv[1])))
    return closest[0]

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: hexToStr.py <hex> <bin_count>")
    else:
        hex_code = sys.argv[1]
        bin_count = int(sys.argv[2])
        print(find_closest_color(hex_code, bin_count))