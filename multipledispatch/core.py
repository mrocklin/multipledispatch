from contextlib import contextmanager
from warnings import warn
from .conflict import ordering


class Dispatcher(object):
    __slots__ = 'name', 'funcs', 'ordering', '_cache'
    def __init__(self, name):
        self.name = name
        self.funcs = dict()
        self._cache = dict()

    def add(self, signature, func):
        self.funcs[signature] = func
        self.ordering = ordering(self.funcs)
        self._cache.clear()

    def __call__(self, *args, **kwargs):
        types = tuple([type(arg) for arg in args])
        func = self.resolve(types)
        return func(*args, **kwargs)


    def resolve(self, types):
        if types in self._cache:
            return self._cache[types]
        elif types in self.funcs:
            self._cache[types] = self.funcs[types]
            return self.funcs[types]

        n = len(types)
        for signature in self.ordering:
            if all(len(signature) == n and issubclass(typ, sig)
                    for typ, sig in zip(types, signature)):
                result = self.funcs[signature]
                self._cache[types] = result
                return result
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
