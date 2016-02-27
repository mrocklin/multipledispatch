""" A Python 3.x-only annotation test module

This module is intended to be used only from Python 3.x, as it
contains code that is invalid syntax for Python 2.x, and thus
can't be loaded as part of any Python 2.x test suite.
"""
from multipledispatch import core
from multipledispatch import dispatch
from multipledispatch.utils import raises


def test_get_types_from_annotations():
    def f(x: int):
        return x

    def g(x: int, y: float, z: str):
        return (x, y, z)

    def h(x):
        return x

    assert [x.__name__ for x in core.get_types_from_annotations(f)] == [
        'int']
    assert [x.__name__ for x in core.get_types_from_annotations(g)] == [
        'int', 'float', 'str']
    assert [x.__name__ for x in core.get_types_from_annotations(h)] == []


def test_dispatch_on_annotations():
    def f(x: int, y: float, z: str):
        return (x, y, z)

    def g(x, y, z):
        return (x, y, z)

    anns = core.dispatch_on_annotations(f).funcs.keys()
    types = core.dispatch_on_types((int, float, str))(f).funcs.keys()
    assert anns == types


def test_multipledispatch():
    @dispatch
    def f(x: int, y: int):
        return x + y

    @dispatch
    def f(x: float, y: float):
        return x - y

    assert f(1, 2) == 3
    assert f(1.0, 2.0) == -1.0


class A(object): pass
class B(object): pass
class C(A): pass
class D(C): pass
class E(C): pass


def test_inheritance():
    @dispatch
    def f(x: A):
        return 'a'

    @dispatch
    def f(x: B):
        return 'b'

    assert f(A()) == 'a'
    assert f(B()) == 'b'
    assert f(C()) == 'a'


def test_inheritance_and_multiple_dispatch():
    @dispatch
    def f(x: A, y: A):
        return type(x), type(y)

    @dispatch
    def f(x: A, y: B):
        return 0

    assert f(A(), A()) == (A, A)
    assert f(A(), C()) == (A, C)
    assert f(A(), B()) == 0
    assert f(C(), B()) == 0
    assert raises(NotImplementedError, lambda: f(B(), B()))


def test_methods():
    class Foo(object):
        @dispatch
        def f(self, x: float):
            return x - 1

        @dispatch
        def f(self, x: int):
            return x + 1

        @dispatch
        def g(self, x: int):
            return x + 3


    foo = Foo()
    assert foo.f(1) == 2
    assert foo.f(1.0) == 0.0
    assert foo.g(1) == 4
