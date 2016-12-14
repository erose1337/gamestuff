from os import urandom

def prng(amount):
    output = 0
    for count, byte in enumerate(bytearray(urandom(amount))):
        output |= (byte << (count * 8))
    return output    

def random_from_range(minimum, maximum, prng=prng):
    assert minimum < maximum, (minimum, maximum)
    values = range(minimum, maximum)    
    return values[prng(16) % len(values)]
    
def test_random_from_range():
    outputs = []
    for count in range(256):
        outputs.append(random_from_range(0, 256, prng))
    print len(set(outputs))
    
if __name__ == "__main__":
    test_random_from_range()
    