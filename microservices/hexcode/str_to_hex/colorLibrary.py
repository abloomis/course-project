# use webcolors library for a quick name to hex conversion tool
#   note that the library only has one-word names (i.e. 'skyblue' 
#   but not 'sky blue')
from webcolors import name_to_hex

def color_name_to_hex(color_name):

  try:
    hex_code = name_to_hex(color_name)
    return hex_code
  except ValueError:
    return None