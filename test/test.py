from multipledispatch2 import dispatch

class A: pass
class B: pass
class C: pass
class D(A,B): pass
class E(A,C): pass
class F(B,C): pass
class G(A,B,C): pass
class H(A,C): pass

@dispatch
def test(_: A):
    return 'A'

@dispatch
def test(_: D):
    return 'D'

@dispatch
def test(_: (B, E)):
    return '(B, E)'

@dispatch
def test(_: [B, C]):
    return '[B, C]'

@dispatch
def test(_: [A, B, C]):
    return '[A, B, C]'

@dispatch
def test(_: [A, (B, C)]):
    return '[A, (B, C)]'

assert test(A()) == 'A'
assert test(D()) == 'D'
assert test(B()) == '(B, E)'
assert test(G()) == '[A, B, C]'
assert test(F()) == '[B, C]'
assert test(H()) == '[A, (B, C)]'
