from multipledispatch import dispatch
from multipledispatch.compatibility import raises
from pytest import xfail


def test_singledispatch():
    @dispatch
    def f(x: int):
        return x + 1

    @dispatch
    def g(x: int):
        return x + 2

    @dispatch
    def f(x: float):
        return x - 1

    assert f(1) == 2
    assert g(1) == 3
    assert f(1.0) == 0

    assert raises(NotImplementedError, lambda: f('hello'))


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


def test_competing_solutions():
    @dispatch
    def h(x: A):
        return 1

    @dispatch
    def h(x: C):
        return 2

    assert h(D()) == 2


def test_competing_multiple():
    @dispatch
    def h(x: A, y: B):
        return 1

    @dispatch
    def h(x: C, y: B):
        return 2

    assert h(D(), B()) == 2


def test_competing_ambiguous():
    @dispatch
    def f(x: A, y: C):
        return 2

    @dispatch
    def f(x: C, y: A):
        return 2

    assert f(A(), C()) == f(C(), A()) == 2
    # assert raises(Warning, lambda : f(C(), C()))


def test_caching_correct_behavior():
    @dispatch
    def f(x: A):
        return 1

    assert f(C()) == 1

    @dispatch
    def f(x: C):
        return 2

    assert f(C()) == 2


def test_union_types():
    @dispatch
    def f(x: (A, C)):
        return 1

    assert f(A()) == 1
    assert f(C()) == 1


"""
Fails
def test_dispatch_on_dispatch():
    @dispatch(A)
    @dispatch(C)
    def q(x):
        return 1

    assert q(A()) == 1
    assert q(C()) == 1
"""


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


def test_methods_multiple_dispatch():
    class Foo(object):
        @dispatch
        def f(x: A, y: A):
            return 1

        @dispatch
        def f(x: A, y: A):
            return 2


    foo = Foo()
    assert foo.f(A(), A()) == 1
    assert foo.f(A(), C()) == 2
    assert foo.f(C(), C()) == 2
