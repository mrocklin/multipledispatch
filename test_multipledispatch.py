from multipledispatch import dispatch

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


def test_inheritance():
    class A(object): pass
    class B(object): pass
    class C(A): pass

    @dispatch(A)
    def f(x):
        return 'a'

    @dispatch(B)
    def f(x):
        return 'b'

    assert f(A()) == 'a'
    assert f(B()) == 'b'
    assert f(C()) == 'a'
