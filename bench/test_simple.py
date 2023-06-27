from multipledispatch import dispatch


@dispatch(int)
def isint(x):
    return True


@dispatch(object)
def isint(x):
    return False


def test_simple():
    for _ in range(100000):
        assert isint(5)
        assert not isint("a")
