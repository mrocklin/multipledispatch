from multipledispatch.conflict import *


class A(object): pass
class B(A): pass
class C(object): pass


def test_supercedes():
    assert supercedes([B], [A])
    assert supercedes([B, A], [A, A])
    assert not supercedes([B, A], [A, B])
    assert not supercedes([A], [B])


def test_consistent():
    assert consistent([A], [A])
    assert consistent([B], [B])
    assert not consistent([A], [C])
    assert consistent([A, B], [A, B])
    assert consistent([B, A], [A, B])
    assert not consistent([B, A], [B])
    assert not consistent([B, A], [B, C])


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

def test_ambiguous():
    assert not ambiguous([A], [A])
    assert not ambiguous([A], [B])
    assert not ambiguous([B], [B])
    assert not ambiguous([A, B], [B, B])
    assert ambiguous([A, B], [B, A])


def test_ambiguities():
    signatures = [[A], [B], [A, B], [B, A], [A, C]]
    expected = set([((A, B), (B, A))])
    result = ambiguities(signatures)
    assert set(map(tuple, expected)) == set(map(tuple, result))
