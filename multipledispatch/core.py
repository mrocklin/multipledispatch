from contextlib import contextmanager
import inspect
from warnings import warn
import sys

from .dispatcher import Dispatcher, MethodDispatcher, ambiguity_warn


global_namespace = dict()


def dispatch(*types, **kwargs):
    """ Dispatch function on the types of the inputs

    For Python 2 and 3, supports dispatch on all non-keyword arguments. For
    Python 3+ only, supports dispatch on annotations.

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

    Example usage for Python 3 (which can't be entered as doctests,
    since Python 2 would fail tp parse it):

    @dispatch
    def f(x: int):
        return x + 3

    @dispatch
    def f(x: float):
        return x + 3.0

    Calling these functions as f(3) and f(3.0) would return 6 and 6.0,
    respectively.
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
        return dispatch_on_types(*types, frame=frame, **kwargs)


def dispatch_on_types(*types, **kwargs):
    """ Dispatch based on the types that are provided as arguments.
    """
    namespace = kwargs.get('namespace', global_namespace)
    on_ambiguity = kwargs.get('on_ambiguity', ambiguity_warn)

    types = tuple(types)
    frame = kwargs.get('frame', None)
    def _(func):
        name = func.__name__
        if ismethod(func):
            dispatcher = frame.f_locals.get(name,
                MethodDispatcher(name))
        else:
            if name not in namespace:
                namespace[name] = Dispatcher(name)
            dispatcher = namespace[name]

        dispatcher.add(types, func, on_ambiguity=on_ambiguity)
        return dispatcher
    return _


def get_types_from_annotations(fn):
    """ This function has been separated out in order to make testing cleaner.
    It is intended only for use by dispatch_on_annotations.

    This should only ever be called by Python 3.4.
    """
    argspec = inspect.getfullargspec(fn)
    if ismethod(fn):
        args = argspec.args[1:]
    else:
        args = argspec.args
    anns = argspec.annotations
    return [anns.get(a) for a in args if anns.get(a)]


def dispatch_on_annotations(fn, **kwargs):
    """ Dispatch types that are calculated from from fn's annotation.

    This should only ever be called by Python 3.4.
    """
    if sys.version_info[0] >= 3:
        types = get_types_from_annotations(fn)
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
