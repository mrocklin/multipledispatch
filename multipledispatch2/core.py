from contextlib import contextmanager
from warnings import warn
import inspect
from .dispatcher import Dispatcher, MethodDispatcher, ambiguity_warn

class AnnotationMustBeTypeError(TypeError):
    pass

global_namespace = dict()


def dispatch(func=None, **kwargs):
    """ Dispatch function on the types of the inputs

    Supports dispatch on all non-keyword arguments.

    Collects implementations based on the function name.  Ignores namespaces.

    If ambiguous type signatures occur a warning is raised when the function is
    defined suggesting the additional method to break the ambiguity.

    Examples
    --------

    >>> @dispatch
    ... def f(x: int) -> int:
    ...     return x + 1

    >>> @dispatch
    ... def f(x: float) -> int:
    ...     return x - 1

    >>> f(3)
    4
    >>> f(3.0)
    2.0

    Specify an isolated namespace with the namespace keyword argument

    >>> my_namespace = dict()
    >>> @dispatch(namespace=my_namespace)
    ... def foo(x: int) -> int:
    ...     return x + 1

    Dispatch on instance methods within classes

    >>> class MyClass(object):
    ...     @dispatch
    ...     def __init__(self, data: list):
    ...         self.data = data
    ...     @dispatch
    ...     def __init__(self, datum: int):
    ...         self.data = [datum]
    """
    namespace = kwargs.get('namespace', global_namespace)
    on_ambiguity = kwargs.get('on_ambiguity', ambiguity_warn)

    def _(func):
        name = func.__name__

        method = ismethod(func)
        if method:
            dispatcher = inspect.currentframe().f_back.f_locals.get(name,
                MethodDispatcher(name))
        else:
            if name not in namespace:
                namespace[name] = Dispatcher(name)
            dispatcher = namespace[name]

        dispatcher.add(get_types(inspect.signature(func).parameters, method=method), func, on_ambiguity=on_ambiguity)
        return dispatcher

    if func:
        return _(func)
    else:
        return _

def get_types(parameters, method):
    types = []
    for idx, arg in enumerate(parameters.values()):
        if idx == 0 and method:
            continue

        if arg.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            if arg.annotation is inspect._empty:
                types.append(object)
            elif isinstance(arg.annotation, type):
                types.append(arg.annotation)
            elif isinstance(arg.annotation, tuple) and all([isinstance(typ, type) for typ in arg.annotation]):
                types.append(arg.annotation)
            else:
                raise AnnotationMustBeTypeError('{}\'s annotation must be a type, but got {}'.format(arg.name, arg.annotation))
        else:
            continue
    return tuple(types)

def ismethod(func):
    """ Is func a method?

    Note that this has to work as the method is defined but before the class is
    defined.  At this stage methods look like functions.
    """
    spec = inspect.signature(func)
    return spec and spec.parameters and list(spec.parameters)[0] == 'self'
