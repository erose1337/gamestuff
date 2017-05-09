import random
from os import urandom as random_bytes

def random_from_range(_min, _max):
    return random.randrange(_min, _max)
        
def random_selection(container, size=None):
    size = len(container) if size is None else size
    return container[random_from_range(0, size)]
            
def test_random_from_range():
    outputs = []    
    for count in range(256):
        outputs.append(random_from_range(0, 256))        
    print len(set(outputs))
   
    
if __name__ == "__main__":
    test_random_from_range()
    