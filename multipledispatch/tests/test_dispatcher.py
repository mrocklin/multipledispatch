from multipledispatch.dispatcher import Dispatcher

def test_dispatcher():
    f = Dispatcher('f')
    inc = lambda x: x + 1
    dec = lambda x: x - 1
    f.add((int,), inc)
    f.add((float,), dec)

    assert f.resolve((int,)) == inc

    assert f(1) == 2
    assert f(1.0) == 0.0
