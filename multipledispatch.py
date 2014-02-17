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
        matches = []
        n = len(types)
        for signature, func in self.funcs.items():
            if len(signature) == n and all(map(issubclass, types, signature)):
                matches.append(func)
        if len(matches) == 1:
            return matches[0]

    def __call__(self, *args, **kwargs):
        func = self.resolve(*args, **kwargs)
        return func(*args, **kwargs)

dispatchers = dict()

def dispatch(*types):
    def _(func):
        name = func.func_name
        if name not in dispatchers:
            dispatchers[name] = Dispatcher(name)
        dispatchers[name].add(types, func)
        return dispatchers[name]
    return _
