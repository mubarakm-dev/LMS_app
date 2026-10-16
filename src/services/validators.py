import re
import random
import string

def validate_email(email):
    pattern = r"^[\w\.]+@[\w\.]+\.[\w]{2,}$"
   
    if re.match(pattern, email):
        return True
    else:
         return False

def validate_password(password):
    pattern = r"(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[\W]).{8,}"
    if re.match(pattern, password):
        return True
    else:
        return False




def suggest_password(length=12):
    pools = [string.ascii_uppercase, string.ascii_lowercase, string.digits, "!@#$%^&*"]

    chars = []
    for pool in pools:
        chars.append(random.choice(pool))
    allowed = "".join(pools)

    remaining = length - len(chars)
    for i in range(remaining):
        chars.append(random.choice(allowed))

    random.shuffle(chars)
    return "".join(chars)
