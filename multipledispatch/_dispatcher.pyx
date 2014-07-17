from .conflict import ordering
from .dispatcher import str_signature

from cpython.dict cimport PyDict_GetItem, PyDict_SetItem
from cpython.object cimport PyObject_Call
from cpython.ref cimport PyObject, Py_INCREF
from cpython.tuple cimport (PyTuple_GET_ITEM, PyTuple_GET_SIZE, PyTuple_New,
                            PyTuple_SET_ITEM)


cdef class DispatcherBase:
    def __call__(self, *args, **kwargs):
        cdef PyObject *obj
        cdef object val
        cdef Py_ssize_t i, N = PyTuple_GET_SIZE(args)
        if N == 1:
            types = type(<object>PyTuple_GET_ITEM(args, 0))
        else:
            types = PyTuple_New(N)
            for i in range(N):
                val = type(<object>PyTuple_GET_ITEM(args, i))
                Py_INCREF(val)
                PyTuple_SET_ITEM(types, i, val)

        obj = PyDict_GetItem(self._cache, types)
        if obj is not NULL:
            return PyObject_Call(<object>obj, args, kwargs)
        elif N == 1:
            # *Always* pass a tuple to `self.resolve`
            val = self.resolve((types,))
        else:
            val = self.resolve(types)
        PyDict_SetItem(self._cache, types, val)
        return PyObject_Call(val, args, kwargs)

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

    def __reduce__(self):
        return (type(self), (self.name,), self.funcs)

    def __setstate__(self, state):
        self.funcs = state
        self._cache = {}
        self.ordering = ordering(self.funcs)


cdef class MethodDispatcherBase(DispatcherBase):
    def __get__(self, instance, owner):
        self.obj = instance
        self.cls = owner
        return self

    def __call__(self, *args, **kwargs):
        cdef PyObject *obj
        cdef object val
        cdef Py_ssize_t i, N = PyTuple_GET_SIZE(args)
        types = PyTuple_New(N)  # = tuple([type(arg) for arg in args])
        selfargs = PyTuple_New(N + 1)  # = (self.obj,) + args
        Py_INCREF(self.obj)
        PyTuple_SET_ITEM(selfargs, 0, self.obj)
        for i in range(N):
            val = <object>PyTuple_GET_ITEM(args, i)
            Py_INCREF(val)
            PyTuple_SET_ITEM(selfargs, i + 1, val)
            val = type(val)
            Py_INCREF(val)
            PyTuple_SET_ITEM(types, i, val)

        obj = PyDict_GetItem(self._cache, types)
        if obj is not NULL:
            return PyObject_Call(<object>obj, selfargs, kwargs)
        else:
            val = self.resolve(types)
            PyDict_SetItem(self._cache, types, val)
            return PyObject_Call(val, selfargs, kwargs)
