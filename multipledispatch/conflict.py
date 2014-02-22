def supercedes(a, b):
    return len(a) == len(b) and all(map(issubclass, a, b))


def consistent(a, b):
    return (len(a) == len(b) and
            all(issubclass(aa, bb) or issubclass(bb, aa)
                           for aa, bb in zip(a, b)))


def ambiguous(a, b):
    return consistent(a, b) and not (supercedes(a, b) or supercedes(b, a))


def ambiguities(signatures):
    return set([(tuple(a), tuple(b)) for a in signatures
                                     for b in signatures
                                     if a < b and ambiguous(a, b)])


def remove_obsolete(signatures):
    return [a for a in signatures
              if not any(len(a) == len(b) and supercedes(b, a)
                         for b in signatures if b is not a)]


def super_signature(signatures):
    n = len(signatures[0])
    assert all(len(s) == n for s in signatures)

    return [max([sig[i].mro() for sig in signatures], key=len)[0]
               for i in range(n)]



def conflict(signatures):
    n = len(signatures[0])
    assert len(set(map(len, signatures))) == n

    edges = set((a, b) for a in signatures
                       for b in signatures
                       if any(issubclass(aa, bb) for aa, bb in zip(a, b)))
