from warnings import warn
import inspect

import copy

from .conflict import ordering, ambiguities, super_signature, AmbiguityWarning
from .utils import expand_tuples

import itertools as itl
import pytypes
import typing


class MDNotImplementedError(NotImplementedError):
    """ A NotImplementedError for multiple dispatch """


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


def halt_ordering():
    """Deprecated interface to temporarily disable ordering.
    """
    warn(
        'halt_ordering is deprecated, you can safely remove this call.',
        DeprecationWarning,
    )


def restart_ordering(on_ambiguity=ambiguity_warn):
    """Deprecated interface to temporarily resume ordering.
    """
    warn(
        'restart_ordering is deprecated, if you would like to eagerly order'
        'the dispatchers, you should call the ``reorder()`` method on each'
        ' dispatcher.',
        DeprecationWarning,
    )


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
    __slots__ = '__name__', 'name', 'funcs', 'annotations', '_ordering', '_cache', 'doc'

    def __init__(self, name, doc=None):
        self.name = self.__name__ = name
        self.funcs = {}
        self.annotations = {}
        self.doc = doc

        self._cache = {}

    def register(self, *types, **kwargs):
        """ register dispatcher with new implementation

        >>> f = Dispatcher('f')
        >>> @f.register(int)
        ... def inc(x):
        ...     return x + 1

        >>> @f.register(float)
        ... def dec(x):
        ...     return x - 1

        >>> @f.register(list)
        ... @f.register(tuple)
        ... def reverse(x):
        ...     return x[::-1]

        >>> f(1)
        2

        >>> f(1.0)
        0.0

        >>> f([1, 2, 3])
        [3, 2, 1]
        """
        def _(func):
            self.add(types, func, **kwargs)
            return func
        return _

    @classmethod
    def get_func_params(cls, func):
        if hasattr(inspect, "signature"):
            sig = inspect.signature(func)
            return sig.parameters.values()

    @classmethod
    def get_func_annotations(cls, func):
        """ get annotations of function positional parameters
        """
        params = cls.get_func_params(func)
        if params:
            Parameter = inspect.Parameter

            params = (param for param in params
                      if param.kind in
                      (Parameter.POSITIONAL_ONLY,
                       Parameter.POSITIONAL_OR_KEYWORD))

            annotations = tuple(
                param.annotation
                for param in params)

            if all(ann is not Parameter.empty for ann in annotations):
                return annotations

    def add(self, signature, func):
        """ Add new types/method pair to dispatcher

        >>> D = Dispatcher('add')
        >>> D.add((int, int), lambda x, y: x + y)
        >>> D.add((float, float), lambda x, y: x + y)
        >>> D.add((typing.Optional[str], ), lambda x: x)

        >>> D(1, 2)
        3
        >>> D('1', 2.0)
        Traceback (most recent call last):
        ...
        NotImplementedError: Could not find signature for add: <str, float>
        >>> D('s')
        's'
        >>> D(None)

        When ``add`` detects a warning it calls the ``on_ambiguity`` callback
        with a dispatcher/itself, and a set of ambiguous type signature pairs
        as inputs.  See ``ambiguity_warn`` for an example.
        """
        # Handle annotations
        if not signature:
            annotations = self.get_func_annotations(func)
            if annotations:
                signature = annotations
        # Make function annotation dict
        if hasattr(func, '__call__'):
            argspec_func = func.__call__
        else:
            argspec_func = func
        argspec = pytypes.getargspecs(argspec_func)
        if pytypes.is_classmethod(argspec_func) or pytypes.is_method(argspec_func):
            arg_names = argspec.args[1:]
        else:
            arg_names = argspec.args

        def process_union(tp):
            if isinstance(tp, tuple):
                t = typing.Union[tuple(process_union(e) for e in tp)]
                return t
            else:
                return tp
        signature = tuple(process_union(tp) for tp in signature)
        import string
        suffix_args = ['__' + c for c in string.ascii_lowercase][:len(signature) - len(arg_names)]
        annotations = dict(zip(list(arg_names) + suffix_args, signature))

        # make a copy of the function (if needed) and apply the function annotations
        # if (not hasattr(func, '__annotations__')) or (not func.__annotations__):
        #     func.__annotations__ = annotations
        # else:
        #     if func.__annotations__ != annotations:
        #         import functools
        #         func = functools.wraps(func)
        #         func.__annotations__ = annotations


        # TODO: REMOVE THIS
        # Handle union types
        #if any(isinstance(typ, tuple) or pytypes.is_Union(typ) for typ in signature):
        #    for typs in expand_tuples(signature):
        #        self.add(typs, func, on_ambiguity)
        #    return

        # TODO: MAKE THIS type or typevar
        for typ in signature:
            try:
                typing.Union[typ]
            except TypeError:
                str_sig = ', '.join(c.__name__ if isinstance(c, type)
                                    else str(c) for c in signature)
                raise TypeError("Tried to dispatch on non-type: %s\n"
                                "In signature: <%s>\n"
                                "In function: %s" %
                                (typ, str_sig, self.name))

        self.funcs[signature] = func
        self.annotations[signature] = annotations
        self._cache.clear()

        try:
            del self._ordering
        except AttributeError:
            pass

    @property
    def ordering(self):
        try:
            return self._ordering
        except AttributeError:
            return self.reorder()

    def reorder(self, on_ambiguity=ambiguity_warn):
        self._ordering = od = ordering(self.funcs)
        amb = ambiguities(self.funcs)
        if amb:
            on_ambiguity(self, amb)
        return od

    def __call__(self, *args, **kwargs):
        try:
            types = tuple([pytypes.deep_type(arg, 1, max_sample=10) for arg in args])
            dargs = args
        except:
            types = tuple([type(arg) for arg in args])
            dargs = None
        try:
            func = self._cache[types]
        except KeyError:
            func = self.dispatch(*types, args=dargs)
            if not func:
                raise NotImplementedError(
                    'Could not find signature for %s: <%s>' %
                    (self.name, str_signature(types)))
            self._cache[types] = func
        try:
            return func(*args, **kwargs)

        except MDNotImplementedError:
            funcs = self.dispatch_iter(*types, args=dargs)
            next(funcs)  # burn first
            for func in funcs:
                try:
                    return func(*args, **kwargs)
                except MDNotImplementedError:
                    pass

            raise NotImplementedError(
                "Matching functions for "
                "%s: <%s> found, but none completed successfully" % (
                    self.name, str_signature(types),
                ),
            )

    def __str__(self):
        return "<dispatched %s>" % self.name
    __repr__ = __str__

    def dispatch(self, *types, args=None):
        """Deterimine appropriate implementation for this type signature

        This method is internal.  Users should call this object as a function.
        Implementation resolution occurs within the ``__call__`` method.

        >>> from multipledispatch import dispatch
        >>> @dispatch(int)
        ... def inc(x):
        ...     return x + 1

        >>> implementation = inc.dispatch(int)
        >>> implementation(3)
        4

        >>> print(inc.dispatch(float))
        None

        See Also:
            ``multipledispatch.conflict`` - module to determine resolution order
        """

        if types in self.funcs:
            return self.funcs[types]

        try:
            return next(self.dispatch_iter(*types, args=args))
        except StopIteration:
            return None

    def dispatch_iter(self, *types, args=None):
        n = len(types)
        for signature in self.ordering:
            if len(signature) == n:
                result = self.funcs[signature]
                annotations = self.annotations[signature]
                def f():
                    pass
                f.__annotations__ = annotations
                try:
                    if pytypes.is_subtype(typing.Tuple[types], typing.Tuple[signature]):
                        yield result
                    elif pytypes.check_argument_types(f, call_args=args):
                        yield result
                except pytypes.InputTypeError:
                    continue

    def resolve(self, types):
        """ Deterimine appropriate implementation for this type signature

        .. deprecated:: 0.4.4
            Use ``dispatch(*types)`` instead
        """
        warn("resolve() is deprecated, use dispatch(*types)",
             DeprecationWarning)

        return self.dispatch(*types)

    def __getstate__(self):
        return {'name': self.name,
                'funcs': self.funcs,
                'annotations': self.annotations}

    def __setstate__(self, d):
        self.name = d['name']
        self.funcs = d['funcs']
        self.annotations = d['annotations']
        self._ordering = ordering(self.funcs)
        self._cache = dict()

    @property
    def __doc__(self):
        docs = ["Multiply dispatched method: %s" % self.name]

        if self.doc:
            docs.append(self.doc)

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

        if other:
            docs.append('Other signatures:\n    ' + '\n    '.join(other))

        return '\n\n'.join(docs)

    def _help(self, *args):
        return self.dispatch(*map(type, args)).__doc__

    def help(self, *args, **kwargs):
        """ Print docstring for the function corresponding to inputs """
        print(self._help(*args))

    def _source(self, *args):
        func = self.dispatch(*map(type, args))
        if not func:
            raise TypeError("No function found")
        return source(func)

    def source(self, *args, **kwargs):
        """ Print source code for the function corresponding to inputs """
        print(self._source(*args))


def source(func):
    s = 'File: %s\n\n' % inspect.getsourcefile(func)
    s = s + inspect.getsource(func)
    return s


class MethodDispatcher(Dispatcher):
    """ Dispatch methods based on type signature

    See Also:
        Dispatcher
    """
    __slots__ = ('obj', 'cls')

    @classmethod
    def get_func_params(cls, func):
        if hasattr(inspect, "signature"):
            sig = inspect.signature(func)
            return itl.islice(sig.parameters.values(), 1, None)

    def __get__(self, instance, owner):
        self.obj = instance
        self.cls = owner
        return self

    def __call__(self, *args, **kwargs):
        types = tuple([type(arg) for arg in args])
        func = self.dispatch(*types)
        if not func:
            raise NotImplementedError('Could not find signature for %s: <%s>' %
                                      (self.name, str_signature(types)))
        return func(self.obj, *args, **kwargs)


def str_signature(sig):
    """ String representation of type signature

    >>> str_signature((int, float))
    'int, float'
    """
    return ', '.join(cls.__name__ for cls in sig)


def warning_text(name, amb):
    """ The text for ambiguity warnings """
    text = "\nAmbiguities exist in dispatched function %s\n\n" % (name)
    text += "The following signatures may result in ambiguous behavior:\n"
    for pair in amb:
        text += "\t" + \
            ', '.join('[' + str_signature(s) + ']' for s in pair) + "\n"
    text += "\n\nConsider making the following additions:\n\n"
    text += '\n\n'.join(['@dispatch(' + str_signature(super_signature(s))
                         + ')\ndef %s(...)' % name for s in amb])
    return text
