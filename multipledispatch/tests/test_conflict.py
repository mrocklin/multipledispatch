from multipledispatch.conflict import *

class A(object): pass
class B(A): pass
class C(object): pass

def test_supercedes():
    assert supercedes([B], [A])
    assert supercedes([B, A], [A, A])
    assert not supercedes([B, A], [A, B])
    assert not supercedes([A], [B])


def test_remove_obsolete():
    signatures = [[A], [B], [A, A], [B, A], [A, B]]
    expected = [[B], [A, B], [B, A]]
    result = remove_obsolete(signatures)
    assert set(map(tuple, result)) == set(map(tuple, expected))


def test_super_signature():
    assert super_signature([[A]]) == [A]
    assert super_signature([[A], [B]]) == [B]
    assert super_signature([[A, B], [B, A]]) == [B, B]
    assert super_signature([[A, A, B], [A, B, A], [B, A, A]]) == [B, B, B]
