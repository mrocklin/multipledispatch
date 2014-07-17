cdef class DispatcherBase:
    cdef public object name
    cdef public object funcs
    cdef public object ordering
    cdef public object _cache


cdef class MethodDispatcherBase(DispatcherBase):
    cdef public object obj
    cdef public object cls
