from contextlib import contextmanager
from warnings import warn
from .conflict import ordering, ambiguities, super_signature, AmbiguityWarning


class Dispatcher(object):
    """ Dispatch methods based on type signature

    Use ``multipledispatch.dispatch`` to add implementations

    Examples
    --------

    >>> @dispatch(int)
    ... def f(x):
    ...     return x + 1

    >>> @dispatch(float)
    ... def f(x):
    ...     return x - 1

    >>> f(3)
    4
    >>> f(3.0)
    2.0
    """
    __slots__ = 'name', 'funcs', 'ordering', '_cache'

    def __init__(self, name):
        self.name = name
        self.funcs = dict()
        self._cache = dict()

    def add(self, signature, func):
        """ Add new types/method pair to dispatcher """
        self.funcs[signature] = func
        self.ordering = ordering(self.funcs)
        amb = ambiguities(self.funcs)
        if amb:
            warn(warning_text(self.name, amb), AmbiguityWarning)
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
    """ Dispatch function on the types of the inputs

    Supports dispatch on all non-keyword arguments.

    Collects implementations based on the function name.  Ignores namespaces.

    If ambiguous type signatures occur a warning is raised when the function is
    defined suggesting the additional method to break the ambiguity.

    Examples
    --------

    >>> @dispatch(int)
    ... def f(x):
    ...     return x + 1

    >>> @dispatch(float)
    ... def f(x):
    ...     return x - 1

    >>> f(3)
    4
    >>> f(3.0)
    2.0
    """
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


def warning_text(name, amb):
    text = "\nAmbiguities exist in dispatched function %s\n\n"%(name)
    text += "The following signatures may result in ambiguous behavior:\n"
    for pair in amb:
        text += "\t" + ', '.join('['+str_signature(s)+']' for s in pair) + "\n"
    text += "\n\nConsider making the following additions:\n\n"
    text += '\n\n'.join(['@dispatch(' + str_signature(super_signature(s))
                      + ')\ndef %s(...)'%name for s in amb])
    return text
