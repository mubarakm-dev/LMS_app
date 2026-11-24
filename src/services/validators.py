import re
import random
import unicodedata
import string

def validate_email(email):
    pattern = r"^[\w\.]+@[\w\.]+\.[\w]{2,}$"
   
    if re.match(pattern, email):
        return True
    else:
         return False

NAME_MESSAGE = (
    "First and last names must be 2 to 50 characters and can only contain "
    "letters, spaces, hyphens and apostrophes."
)


def validate_name(name):
    name = name.strip()
    if not 2 <= len(name) <= 50:
        return False

    for ch in name:
        if not (ch.isalpha() or unicodedata.category(ch).startswith("M") or ch in " -'’"):
            return False

    return name[0].isalpha() and name[-1].isalpha()


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
