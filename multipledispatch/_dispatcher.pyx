import cython

from cpython.dict cimport PyDict_GetItem, PyDict_SetItem
from cpython.object cimport PyObject_Call
from cpython.ref cimport PyObject, Py_INCREF
from cpython.tuple cimport PyTuple_GET_ITEM, PyTuple_GET_SIZE, PyTuple_New, PyTuple_SET_ITEM


@cython.binding(True)
def __call__(self, *args, **kwargs):
    cdef object val
    cdef Py_ssize_t i, N
    N = PyTuple_GET_SIZE(args)
    types = PyTuple_New(N)
    for i in range(N):
        val = type(<object>PyTuple_GET_ITEM(args, i))
        Py_INCREF(val)
        PyTuple_SET_ITEM(types, i, val)

    obj = PyDict_GetItem(self._cache, types)
    if obj is not NULL:
        return PyObject_Call(<object>obj, args, kwargs)
    else:
        val = self.resolve(types)
        PyDict_SetItem(self._cache, types, val)
        return PyObject_Call(val, args, kwargs)


@cython.binding(True)
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
    cdef PyObject *obj = PyDict_GetItem(self.funcs, types)
    if obj is not NULL:
        return <object>obj

    n = len(types)
    for signature in self.ordering:
        if len(signature) == n and all(map(issubclass, types, signature)):
            result = self.funcs[signature]
            return result
    raise NotImplementedError('Could not find signature for %s: <%s>' %
                              (self.name, str_signature(types)))


# TODO: import from elsewhere
cdef object str_signature(sig):
    """ String representation of type signature

    >>> str_signature((int, float))
    'int, float'
    """
    return ', '.join([cls.__name__ for cls in sig])
