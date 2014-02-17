from contextlib import contextmanager


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
            winners = [min([(func, indices) for (func, indices)
                                            in scores.items()],
                           key=lambda (f, ind): ind[i])
                       for i in range(len(types))]
            winners = set([func for func, ind in winners])
            if len(winners) != 1:
                raise Warning("Multiple competing implementations found",
                              "Using one at random.")
            return next(iter(winners))
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
