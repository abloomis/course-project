from hexcode_client import convert_color

# call the convert_color function from the client file, which is
#   wrapped in this function
def test_microservice(input_value, bins=None):
    result = convert_color(input_value, bins)
    print(f"Input: {input_value} (bins={bins}) -> Result: {result}")

# some example tests
if __name__ == '__main__':
    # strToHex
    test_microservice('blue')
    test_microservice('gray')
    test_microservice('invalidcolor')  # should return error

    # hexToStr
    test_microservice('#02A3B4', 6)
    test_microservice('#B3809D', 3)
    test_microservice('82CF42', 3)     # hex without hash
    test_microservice('#F2FBF7', 15)

    # hexToStr without bins param (should return error)
    test_microservice('#123456')