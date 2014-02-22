from multipledispatch.conflict import *

class A(object): pass
class B(A): pass
class C(object): pass

def test_supercedes():
    assert supercedes([B], [A])
