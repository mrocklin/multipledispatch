from multipledispatch import core
from multipledispatch import dispatch
from multipledispatch.utils import raises


def test_get_types_from_annotations():
    def f(x: int):
        return x

    def g(x: int, y: float, z: str):
        return (x, y, z)

    assert [x.__name__ for x in core.get_types_from_annotations(f)] == [
        'int']
    assert [x.__name__ for x in core.get_types_from_annotations(g)] == [
        'int', 'float', 'str']


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
