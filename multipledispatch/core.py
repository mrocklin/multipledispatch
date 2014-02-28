from contextlib import contextmanager
from warnings import warn
from .conflict import (ordering, ambiguities, super_signature,
        AmbiguityWarning, issubclass_cmp)
import inspect


class Dispatcher(object):
    """ Dispatch methods based on type signature

    Use ``dispatch`` to add implementations

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
    __slots__ = 'name', 'funcs', 'ordering', 'vararg_funcs', 'vararg_ordering', '_cache'

    def __init__(self, name):
        self.name = name
        self.funcs = dict()
        self.ordering = list()
        self.vararg_funcs = dict()
        self.vararg_ordering = list()
        self._cache = dict()

    def add(self, signature, func):
        """ Add new types/method pair to dispatcher

        >>> D = Dispatcher('add')
        >>> D.add((int, int), lambda x, y: x + y)
        >>> D.add((float, float), lambda x, y: x + y)

        >>> D(1, 2)
        3
        >>> D(1, 2.0)
        Traceback (most recent call last):
        ...
        NotImplementedError
        """
        self.funcs[signature] = func
        self.ordering = ordering(self.funcs)
        amb = ambiguities(self.funcs)
        if amb:
            warn(warning_text(self.name, amb), AmbiguityWarning)
        self._cache.clear()

    def add_varargs(self, typ, func):
        self.vararg_funcs[typ] = func
        self.vararg_ordering = sorted(self.vararg_funcs,
                                      cmp=issubclass_cmp,
                                      reverse=True)
        self._cache.clear()

    def __call__(self, *args, **kwargs):
        types = tuple([type(arg) for arg in args])
        func = self.resolve(types)
        return func(*args, **kwargs)

    def __str__(self):
        return "<dispatched %s>" % self.name
    __repr__ = __str__

    def resolve(self, types):
        """ Deterimine appropriate implementation for this type signature

        This method is internal.  Users should call this object as a function.
        Implementation resolution occurs within the ``__call__`` method.

        >>> @dispatch(int)
        ... def inc(x):
        ...     return x + 1

        >>> implementation = inc.resolve((int,))
        >>> implementation(3)
        4

        >>> inc.resolve((float,))
        Traceback (most recent call last):
        ...
        NotImplementedError

        See Also:
            ``multipledispatch.conflict`` - module to determine resolution order
        """

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
        for sig in self.vararg_ordering:
            if all(issubclass(typ, sig) for typ in types):
                result = self.vararg_funcs[sig]
                self._cache[types] = result
                return result
        raise NotImplementedError()


class MethodDispatcher(Dispatcher):
    """ Dispatch methods based on type signature

    See Also:
        Dispatcher
    """
    def __get__(self, instance, owner):
        self.obj = instance
        self.cls = owner
        return self

    def __call__(self, *args, **kwargs):
        types = tuple([type(arg) for arg in args])
        func = self.resolve(types)
        return func(self.obj, *args, **kwargs)


global_namespace = dict()


def dispatch(*types, **kwargs):
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

    Specify an isolated namespace with the namespace keyword argument

    >>> my_namespace = dict()
    >>> @dispatch(int, namespace=my_namespace)
    ... def foo(x):
    ...     return x + 1

    Dispatch on instance methods within classes

    >>> class MyClass(object):
    ...     @dispatch(list)
    ...     def __init__(self, data):
    ...         self.data = data
    ...     @dispatch(int)
    ...     def __init__(self, datum):
    ...         self.data = [datum]
    """
    namespace = kwargs.get('namespace', global_namespace)
    types = tuple(types)
    def _(func):
        name = func.__name__

        if ismethod(func):
            dispatcher = inspect.currentframe().f_back.f_locals.get(name,
                MethodDispatcher(name))
        else:
            if name not in namespace:
                namespace[name] = Dispatcher(name)
            dispatcher = namespace[name]
        if len(types) == 1 and isinstance(types[0], list):
            dispatcher.add_varargs(types[0][0], func)
        else:
            for typs in expand_tuples(types):
                dispatcher.add(typs, func)
        return dispatcher
    return _


def ismethod(func):
    """ Is func a method?

    Note that this has to work as the method is defined but before the class is
    defined.  At this stage methods look like functions.
    """
    spec = inspect.getargspec(func)
    return spec and spec.args and spec.args[0] == 'self'


def expand_tuples(L):
    """

    >>> expand_tuples([1, (2, 3)])
    [(1, 2), (1, 3)]

    >>> expand_tuples([1, 2])
    [(1, 2)]
    """
    if not L:
        return [()]
    elif not isinstance(L[0], tuple):
        rest = expand_tuples(L[1:])
        return [(L[0],) + t for t in rest]
    else:
        rest = expand_tuples(L[1:])
        return [(item,) + t for t in rest for item in L[0]]


def str_signature(sig):
    """ String representation of type signature

    >>> str_signature((int, float))
    'int, float'
    """
    return ', '.join(cls.__name__ for cls in sig)


def warning_text(name, amb):
    """ The text for ambiguity warnings """
    text = "\nAmbiguities exist in dispatched function %s\n\n"%(name)
    text += "The following signatures may result in ambiguous behavior:\n"
    for pair in amb:
        text += "\t" + ', '.join('['+str_signature(s)+']' for s in pair) + "\n"
    text += "\n\nConsider making the following additions:\n\n"
    text += '\n\n'.join(['@dispatch(' + str_signature(super_signature(s))
                      + ')\ndef %s(...)'%name for s in amb])
    return text
