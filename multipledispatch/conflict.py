from .utils import _toposort, groupby, VariadicSignatureType


class AmbiguityWarning(Warning):
    pass


def supercedes(a, b):
    """ A is consistent and strictly more specific than B """
    if len(a) < len(b):
        # only case is if a is empty and b is variadic
        return (len(a) == 0 and
                len(b) == 1 and
                isinstance(b[-1], VariadicSignatureType))
    elif len(a) == len(b):
        return all(map(issubclass, a, b))
    else:
        # len(a) > len(b)
        p1 = 0
        p2 = 0
        while p1 < len(a) and p2 < len(b):
            if (not isinstance(a[p1], VariadicSignatureType) and
                    not isinstance(b[p2], VariadicSignatureType)):
                if not issubclass(a[p1], b[p2]):
                    return False
                p1 += 1
                p2 += 1
            elif isinstance(a[p1], VariadicSignatureType):
                assert p1 == len(a) - 1
                return p2 == len(b) - 1 and issubclass(a[p1], b[p2])
            elif isinstance(b[p2], VariadicSignatureType):
                assert p2 == len(b) - 1
                if not issubclass(a[p1], b[p2]):
                    return False
                p1 += 1
        return p2 == len(b) - 1 and p1 == len(a)


def consistent(a, b):
    """ It is possible for an argument list to satisfy both A and B """
    def check_variadic_consistency(a, b):
        if (len(a) == 0 or
            (not isinstance(a[-1], VariadicSignatureType) and
             not isinstance(b[-1], VariadicSignatureType))):
            return True
        else:
            return a[-1] == b[-1]

    return (len(a) == len(b) and
            all(issubclass(aa, bb) or issubclass(bb, aa)
                for aa, bb in zip(a, b)) and
            check_variadic_consistency(a, b))


def ambiguous(a, b):
    """ A is consistent with B but neither is strictly more specific """
    return consistent(a, b) and not (supercedes(a, b) or supercedes(b, a))


def ambiguities(signatures):
    """ All signature pairs such that A is ambiguous with B """
    signatures = list(map(tuple, signatures))
    return set([(a, b) for a in signatures for b in signatures
                if hash(a) < hash(b)
                and ambiguous(a, b)
                and not any(supercedes(c, a) and supercedes(c, b)
                            for c in signatures)])


def super_signature(signatures):
    """ A signature that would break ambiguities """
    n = len(signatures[0])
    assert all(len(s) == n for s in signatures)

    return [max([type.mro(sig[i]) for sig in signatures], key=len)[0]
            for i in range(n)]


def edge(a, b, tie_breaker=hash):
    """ A should be checked before B

    Tie broken by tie_breaker, defaults to ``hash``
    """
    if supercedes(a, b):
        if supercedes(b, a):
            return tie_breaker(a) > tie_breaker(b)
        else:
            return True
    return False


def ordering(signatures):
    """ A sane ordering of signatures to check, first to last

    Topoological sort of edges as given by ``edge`` and ``supercedes``
    """
    signatures = list(map(tuple, signatures))
    edges = [(a, b) for a in signatures for b in signatures if edge(a, b)]
    edges = groupby(lambda x: x[0], edges)
    for s in signatures:
        if s not in edges:
            edges[s] = []
    edges = dict((k, [b for a, b in v]) for k, v in edges.items())
    return _toposort(edges)
