import string
import random

def generateCSVRand(filename, size):
    names = []
    for _ in range(size):
        stringlen = random.randint(1,18)
        characters = string.ascii_letters + string.digits
        name = ''.join(random.choice(characters) for _ in range(stringlen))
        names.append(name)
    with open(filename, "w") as f:
        for name in names:
            f.write(',' + name)
        for name in names:
            f.write('\n')
            f.write(name)
            for _ in range(len(names)):
                randNum1 = str(random.randint(1,12))
                randNum2 = str(random.randint(1,12))
                f.write(',' + randNum1 + '-' + randNum2)

    return

generateCSVRand('ExampleData04.csv', 10)