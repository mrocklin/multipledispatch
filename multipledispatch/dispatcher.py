from warnings import warn
from .conflict import ordering, ambiguities, super_signature, AmbiguityWarning
from .utils import expand_tuples


def ambiguity_warn(dispatcher, ambiguities):
    """ Raise warning when ambiguity is detected

    Parameters
    ----------
    dispatcher : Dispatcher
        The dispatcher on which the ambiguity was detected
    ambiguities : set
        Set of type signature pairs that are ambiguous within this dispatcher

    See Also:
        Dispatcher.add
        warning_text
    """
    warn(warning_text(dispatcher.name, ambiguities), AmbiguityWarning)


_unresolved_dispatchers = set()
_resolve = [True]


def halt_ordering():
    _resolve[0] = False


def restart_ordering(on_ambiguity=ambiguity_warn):
    _resolve[0] = True
    while _unresolved_dispatchers:
        dispatcher = _unresolved_dispatchers.pop()
        dispatcher.reorder(on_ambiguity=on_ambiguity)



class Dispatcher(object):
    """ Dispatch methods based on type signature

    Use ``dispatch`` to add implementations

    Examples
    --------

    >>> from multipledispatch import dispatch
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
        self.ordering = []

    def register(self, *types, **kwargs):
        """ register dispatcher with new implementation

        >>> f = Dispatcher('f')
        >>> @f.register(int)
        ... def f(x):
        ...     return x + 1

        >>> @f.register(float)
        ... def f(x):
        ...     return x - 1

        >>> f(1)
        2

        >>> f(1.0)
        0.0
        """
        def _(func):
            self.add(types, func, **kwargs)
            return self
        return _

    def add(self, signature, func, on_ambiguity=ambiguity_warn):
        """ Add new types/method pair to dispatcher

        >>> D = Dispatcher('add')
        >>> D.add((int, int), lambda x, y: x + y)
        >>> D.add((float, float), lambda x, y: x + y)

        >>> D(1, 2)
        3
        >>> D(1, 2.0)
        Traceback (most recent call last):
        ...
        NotImplementedError: Could not find signature for add: <int, float>

        When ``add`` detects a warning it calls the ``on_ambiguity`` callback
        with a dispatcher/itself, and a set of ambiguous type signature pairs
        as inputs.  See ``ambiguity_warn`` for an example.
        """
        # Handle union types
        if any(isinstance(typ, tuple) for typ in signature):
            for typs in expand_tuples(signature):
                self.add(typs, func, on_ambiguity)
            return

        for typ in signature:
            if not isinstance(typ, type):
                str_sig = ', '.join(c.__name__ if isinstance(c, type)
                                               else str(c) for c in signature)
                raise TypeError("Tried to dispatch on non-type: %s\n"
                                "In signature: <%s>\n"
                                "In function: %s" %
                                (typ, str_sig, self.name))

        self.funcs[signature] = func
        self.reorder(on_ambiguity=on_ambiguity)
        self._cache.clear()

    def reorder(self, on_ambiguity=ambiguity_warn):
        if _resolve[0]:
            self.ordering = ordering(self.funcs)
            amb = ambiguities(self.funcs)
            if amb:
                on_ambiguity(self, amb)
        else:
            _unresolved_dispatchers.add(self)


    def __call__(self, *args, **kwargs):
        types = tuple([type(arg) for arg in args])
        try:
            func = self._cache[types]
        except KeyError:
            func = self.resolve(types)
            self._cache[types] = func
        return func(*args, **kwargs)

    def __str__(self):
        return "<dispatched %s>" % self.name
    __repr__ = __str__

    def resolve(self, types):
        """ Deterimine appropriate implementation for this type signature

        This method is internal.  Users should call this object as a function.
        Implementation resolution occurs within the ``__call__`` method.

        >>> from multipledispatch import dispatch
        >>> @dispatch(int)
        ... def inc(x):
        ...     return x + 1

        >>> implementation = inc.resolve((int,))
        >>> implementation(3)
        4

        >>> inc.resolve((float,))
        Traceback (most recent call last):
        ...
        NotImplementedError: Could not find signature for inc: <float>

        See Also:
            ``multipledispatch.conflict`` - module to determine resolution order
        """

        if types in self.funcs:
            return self.funcs[types]

        n = len(types)
        for signature in self.ordering:
            if len(signature) == n and all(map(issubclass, types, signature)):
                result = self.funcs[signature]
                return result
        raise NotImplementedError('Could not find signature for %s: <%s>' %
                                  (self.name, str_signature(types)))

    def __getstate__(self):
        return {'name': self.name,
                'funcs': self.funcs}

    def __setstate__(self, d):
        self.name = d['name']
        self.funcs = d['funcs']
        self.ordering = ordering(self.funcs)
        self._cache = dict()


    @property
    def __doc__(self):
        doc = " Multiply dispatched method: %s\n\n" % self.name

        docs = []
        other = []
        for sig in self.ordering[::-1]:
            func = self.funcs[sig]
            if func.__doc__:
                s = 'Inputs: <%s>\n' % str_signature(sig)
                s += '-' * len(s) + '\n'
                s += func.__doc__.strip()
                docs.append(s)
            else:
                other.append(str_signature(sig))

        doc += '\n\n'.join(docs)

        if other:
            doc += '\n\nOther signatures:\n    '
            doc += '\n\    '.join(other)

        return doc


class MethodDispatcher(Dispatcher):
    """ Dispatch methods based on type signature

    See Also:
        Dispatcher
    """
    def __get__(self, instance, owner):
        dispatcher = self
        def method(self, *args, **kwargs):
            return dispatcher(self, *args, **kwargs)
        method.__name__ = self.name
        return method.__get__(instance, owner)

    def __call__(self, obj, *args, **kwargs):
        types = tuple([type(arg) for arg in args])
        func = self.resolve(types)
        return func(obj, *args, **kwargs)


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
