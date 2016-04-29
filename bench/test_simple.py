from multipledispatch2 import dispatch

@dispatch
def isint(x: int) -> bool:
    return True

@dispatch
def isint(x) -> bool:
    return False

def test_simple():
    for i in range(100000):
        isint(5)
        isint('a')
