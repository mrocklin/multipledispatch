# import sys

# from nose import SkipTest

from multipledispatch import dispatch
from multipledispatch.dispatcher import Dispatcher


def test_function_annotation_register():
    # if sys.version_info < (3, 3):
    #     raise SkipTest

    f = Dispatcher('f')

    @f.register()
    def inc(x: int):
        return x + 1

    @f.register()
    def inc(x: float):
        return x - 1

    assert f(1) == 2
    assert f(1.0) == 0.0


def test_function_annotation_dispatch():
    # if sys.version_info < (3, 3):
    #     raise SkipTest

    @dispatch()
    def inc(x: int):
        return x + 1

    @dispatch()
    def inc(x: float):
        return x - 1

    assert inc(1) == 2
    assert inc(1.0) == 0.0


def test_function_annotation_dispatch_custom_namespace():
    # if sys.version_info < (3, 3):
    #     raise SkipTest
    namespace = {}

    @dispatch(namespace=namespace)
    def inc(x: int):
        return x + 2

    @dispatch(namespace=namespace)
    def inc(x: float):
        return x - 2

    assert inc(1) == 3
    assert inc(1.0) == -1.0
