from collections import namedtuple
import inspect
import sys

from multipledispatch import compat
from multipledispatch import dispatch
from multipledispatch.dispatcher import MethodDispatcher


class F(object):

    def f(self, x):
        return x


def f(x):
    return x


obj = F()
name = obj.f.__name__


def test_get_method_dispatcher():
    frame = inspect.currentframe().f_back
    kw_dict = {"frame": frame}
    result = compat.get_method_dispatcher(name, frame, kw_dict)

    assert isinstance(result, MethodDispatcher)


def test_get_method_dispatcher_custom():
    class CustomDispatcher(object):
        def __init__(self, name):
            pass

    frame = inspect.currentframe().f_back
    kw_dict = {"frame": frame}
    result = compat.get_method_dispatcher(
        name, frame, kw_dict, CustomDispatcher)

    assert isinstance(result, CustomDispatcher)


def test_get_f_locals():
    frame = inspect.currentframe().f_back
    kw_dict = {"frame": frame}

    if sys.version_info[0] >= 3:
        result = compat.get_f_locals_py3(kw_dict)
    else:
        result = compat.get_f_locals_py2(frame)

    assert type(result) == dict


def test_is_method():
    assert not compat.ismethod(f)
    assert compat.ismethod(obj.f)


def test_get_argspec():
    if sys.version_info[0] >= 3:
        results = (compat.get_argspec_py3(f),
                   compat.get_argspec_py3(obj.f))
        klass = inspect.FullArgSpec
    else:
        results = (compat.get_argspec_py2(f),
                   compat.get_argspec_py2(obj.f))
        klass = inspect.ArgSpec
    print([isinstance(x, klass) for x in results])
