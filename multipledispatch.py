from contextlib import contextmanager
from warnings import warn


class Dispatcher(object):
    __slots__ = 'name', 'funcs'
    def __init__(self, name):
        self.name = name
        self.funcs = dict()

    def add(self, signature, func):
        self.funcs[signature] = func

    def resolve(self, *args, **kwargs):
        types = tuple(map(type, args))
        if types in self.funcs:
            return self.funcs[types]

        matches = dict()
        n = len(types)
        for signature, func in self.funcs.items():
            if len(signature) == n and all(map(issubclass, types, signature)):
                matches[signature] = func
        if len(matches) == 1:
            return matches.values()[0]
        if len(matches) > 1:
            scores = {func: [typ.mro().index(sig)
                                for typ, sig in zip(types, signature)]
                            for signature, func in matches.items()}
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

    def __call__(self, *args, **kwargs):
        func = self.resolve(*args, **kwargs)
        return func(*args, **kwargs)


dispatchers = dict()


def dispatch(*types):
    types = tuple(types)
    def _(func):
        name = func.func_name
        if name not in dispatchers:
            dispatchers[name] = Dispatcher(name)
        dispatchers[name].add(types, func)
        return dispatchers[name]
    return _


def minset(seq, key=lambda x: x):
    """ Find all minimum elements of sequence

    >>> minset(['Cat', 'Dog', 'Camel', 'Mouse'], key=lambda x: x[0])
    set(['Camel', 'Cat'])
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
