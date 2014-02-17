from multipledispatch import dispatch
from pytest import raises

def test_singledispatch():
    @dispatch(int)
    def f(x):
        return x + 1

    @dispatch(float)
    def f(x):
        return x - 1

    assert f(1) == 2
    assert f(1.0) == 0


def test_multipledispatch():
    @dispatch(int, int)
    def f(x, y):
        return x + y

    @dispatch(float, float)
    def f(x, y):
        return x - y

    assert f(1, 2) == 3
    assert f(1.0, 2.0) == -1.0


class A(object): pass
class B(object): pass
class C(A): pass


def test_inheritance():
    @dispatch(A)
    def f(x):
        return 'a'

    @dispatch(B)
    def f(x):
        return 'b'

    assert f(A()) == 'a'
    assert f(B()) == 'b'
    assert f(C()) == 'a'


def test_inheritance_and_multiple_dispatch():
    @dispatch(A, A)
    def f(x, y):
        return type(x), type(y)

    @dispatch(A, B)
    def f(x, y):
        return 0

    assert f(A(), A()) == (A, A)
    assert f(A(), C()) == (A, C)
    assert f(A(), B()) == 0
    assert f(C(), B()) == 0
    assert raises(NotImplementedError, lambda: f(B(), B()))
