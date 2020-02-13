import random
import string

def passwordgenerator(stringLength=8):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

def codegenerator(length=6):
    start_number = 10**(length-1)
    end_number = (10**length)-1
    return random.randint(start_number, end_number)
