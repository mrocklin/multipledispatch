from multipledispatch import dispatch

@dispatch(int)
def isint(x):
    return True

@dispatch(object)
def isint(x):
    return False

def test_simple():
    for i in xrange(100000):
        isint(5)
        isint('a')
