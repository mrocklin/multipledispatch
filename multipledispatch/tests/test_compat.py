import sys
import inspect

from multipledispatch import compat
from multipledispatch import dispatch
from multipledispatch.dispatcher import MethodDispatcher


class F(object):

    def f(self, x):
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
