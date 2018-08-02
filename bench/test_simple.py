import six

from multipledispatch import dispatch


@dispatch(int)
def isint(x):
    return True


@dispatch(object)
def isint(x):
    return False


def test_simple():
    for i in six.moves.xrange(100000):
        assert isint(5)
        assert not isint('a')
