from contextlib import contextmanager

class Dispatcher(object):
    __slots__ = 'name', 'funcs'
    def __init__(self, name):
        self.name = name
        self.funcs = dict()

    def add(self, signature, func):
        self.funcs[signature] = func

    def __call__(self, *args, **kwargs):
        try:
            func = self.funcs[tuple(map(type, args))]
        except KeyError:
            raise NotImplementedError()
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


