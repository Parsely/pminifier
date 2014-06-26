import random

# Used to encode ints to shortened strings
alphabet = '2FQYNEJAUsbGu41zndZTeocMai5H7OIjXkKg8qyt3WC9hLplxfVBm0wSRr6vPD'

def int_to_base62(id):
    """Convert the int id to a user-friendly string using base62"""
    if id < 0:
        raise ValueError("Must supply a positive integer.")
    l = len(alphabet)
    converted = []
    while id != 0:
        id, r = divmod(id, l)
        converted.insert(0, alphabet[r])
    return "".join(converted) or '0'

def base62_to_int(minified):
    """Convert the base62 string back to an int"""
    if set(minified) - set(alphabet):
        raise ValueError("Minified ID contains invalid characters '%s'" % "".join(set(minified) - set(alphabet)))

    s = minified[::-1]
    l = len(alphabet)
    output = 0
    for i, c in enumerate(s):
        output += int(alphabet.index(c) * math.pow(l, i))
    return int(output)

def jitter(num, rate=0.25):
    """Add jitter to a number (e.g. 25% jitter gives (0.75*n, 1.25*n))

    If given an int, returns a rounded int, otherwise returns float.
    """
    if type(num) == int:
        return int(round(num * random.uniform(1-rate, 1+rate)))
    else:
        return num * random.uniform(1-rate, 1+rate)

def unicode_to_str(text, encoding=None, errors='strict'):
    if encoding is None:
        encoding = 'utf-8'
    if isinstance(text, unicode):
        return text.encode(encoding, errors)
    return text
