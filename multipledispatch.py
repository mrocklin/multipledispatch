from contextlib import contextmanager
from warnings import warn


class Dispatcher(object):
    __slots__ = 'name', 'funcs'
    def __init__(self, name):
        self.name = name
        self.funcs = dict()

    def add(self, signature, func):
        self.funcs[signature] = func

    def __call__(self, *args, **kwargs):
        types = tuple(map(type, args))
        func = resolve(self.funcs, types, **kwargs)
        return func(*args, **kwargs)


def resolve(funcs, types, **kwargs):
    if types in funcs:
        return funcs[types]

    n = len(types)
    matches = dict((signature, func) for signature, func in funcs.items()
                                     if len(signature) == n
                                     and all(map(issubclass, types, signature)))
    if len(matches) == 1:
        return next(iter(matches.values()))
    if len(matches) > 1:
        scores = dict((func, [typ.mro().index(sig)
                            for typ, sig in zip(types, signature)])
                        for signature, func in matches.items())
        winners = [minset(scores, key=lambda func: scores[func][i])
                    for i in range(len(types))]
        intersection = set.intersection(*winners)
        if len(intersection) == 1:  # One obvious best choice
            return next(iter(intersection))
        else:
            warn("Multiple competing implementations found"
                 "Using one at random.")
            union = set.union(*winners)
            return next(iter(union))
    raise NotImplementedError()


dispatchers = dict()


def dispatch(*types):
    types = tuple(types)
    def _(func):
        name = func.__name__
        if name not in dispatchers:
            dispatchers[name] = Dispatcher(name)
        dispatchers[name].add(types, func)
        return dispatchers[name]
    return _


def minset(seq, key=lambda x: x):
    """ Find all minimum elements of sequence

    >>> sorted(minset(['Cat', 'Dog', 'Camel', 'Mouse'], key=lambda x: x[0]))
    ['Camel', 'Cat']
    """
    if not seq:
        raise ValueError("Empty input")
    seq = iter(seq)
    first = next(seq)
    best = set([first])
    bestval = key(first)

    for item in seq:
        val = key(item)
        if val < bestval:
            bestval = val
            best.clear()
            best.add(item)
        elif val == bestval:
            best.add(item)
    return best
