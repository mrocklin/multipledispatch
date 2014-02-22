def supercedes(a, b):
    return len(a) == len(b) and all(map(issubclass, a, b))
