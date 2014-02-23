from contextlib import contextmanager
from warnings import warn
from .conflict import ordering, ambiguities, super_signature


class Dispatcher(object):
    __slots__ = 'name', 'funcs', 'ordering', '_cache'
    def __init__(self, name):
        self.name = name
        self.funcs = dict()
        self._cache = dict()

    def add(self, signature, func):
        self.funcs[signature] = func
        self.ordering = ordering(self.funcs)
        amb = ambiguities(self.funcs)
        if amb:
            warn(warning_text(self.name, amb))
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


def warning_text(name, amb):
    text = "\nAmbiguities exist in dispatched function %s\n\n"%(name)
    text += "The following signatures may result in ambiguous behavior:\n"
    for pair in amb:
        text += "\t" + ', '.join('['+str_signature(s)+']' for s in pair) + "\n"
    text += "\n\nConsider making the following additions:\n\n"
    text += '\n\n'.join(['@dispatch(' + str_signature(super_signature(s))
                      + ')\ndef %s(...)'%name for s in amb])
    return text

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


def str_signature(sig):
    return ', '.join(cls.__name__ for cls in sig)


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
