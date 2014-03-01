from contextlib import contextmanager
from warnings import warn
from .conflict import ordering, ambiguities, super_signature, AmbiguityWarning
import inspect
import sys


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

    def __call__(self, *args, **kwargs):
        types = tuple([type(arg) for arg in args])
        func = self.resolve(types)
        return func(*args, **kwargs)

    def __str__(self):
        return "<dispatched %s>" % self.name
    __repr__ = __str__

    @property
    def supported_types(self):
        """ A topologically sorted list of type signatures """
        return self.ordering

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


dispatchers = dict()


def dispatch(*types):
    """
    Dispatch decorator with two modes of use:

    @dispatch(int):
    def f(x):
        return 'int!'

    @dispatch
    def f(x: float):
        return 'float!'
    """
    # if one argument as passed that is not callable and isn't a type, dispatch
    # on annotations
    frame = inspect.currentframe().f_back
    if (len(types) == 1
            and callable(types[0])
            and not isinstance(types[0], type)):
        fn = types[0]
        return dispatch_on_annotations(fn, frame=frame)
    # otherwise dispatch on types
    else:
        return dispatch_on_types(*types, frame=frame)


def dispatch_on_types(*types, **kwargs):
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
    frame = kwargs.get('frame', None)
    def _(func):
        name = func.__name__
        if ismethod(func):
            dispatcher = frame.f_locals.get(name,
                MethodDispatcher(name))
        else:
            if name not in dispatchers:
                dispatchers[name] = Dispatcher(name)
            dispatcher = dispatchers[name]

        for typs in expand_tuples(types):
            dispatcher.add(typs, func)
        return dispatcher
    return _


def dispatch_on_annotations(fn, **kwargs):
    """
    Extract types from fn's annotation (only works in Python 3+)
    """
    if sys.version_info.major >= 3:
        argspec = inspect.getfullargspec(fn)
        args = argspec.args[1:] if ismethod(fn) else argspec.args
        types = [argspec.annotations[a] for a in args]
        return dispatch_on_types(*types, **kwargs)(fn)
    else:
        raise SyntaxError('Annotations require Python 3+.')


def ismethod(func):
    """ Is func a method?

    Note that this has to work as the method is defined but before the class is
    defined.  At this stage methods look like functions.
    """
    try:
        spec = inspect.getargspec(func)
    except:
        spec = inspect.getfullargspec(func)
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

