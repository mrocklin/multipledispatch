from multipledispatch.dispatcher import Dispatcher, MethodDispatcher


def identity(x):
    return x


def inc(x):
    return x + 1


def dec(x):
    return x - 1


def test_dispatcher():
    f = Dispatcher('f')
    f.add((int,), inc)
    f.add((float,), dec)

    assert f.resolve((int,)) == inc

    assert f(1) == 2
    assert f(1.0) == 0.0


def test_dispatcher_as_decorator():
    f = Dispatcher('f')

    @f.register(int)
    def inc(x):
        return x + 1

    @f.register(float)
    def inc(x):
        return x - 1

    assert f(1) == 2
    assert f(1.0) == 0.0


def test_register_instance_method():
    f = MethodDispatcher('f')

    class Test(object):
        @f.register(list)
        def __init__(self, data):
            self.data = data

        @f.register(object)
        def __init__(self, datum):
            self.data = [datum]

    a = Test(3)
    b = Test([3])
    assert a.data == b.data


def test_on_ambiguity():
    f = Dispatcher('f')

    identity = lambda x: x

    ambiguities = [False]
    def on_ambiguity(dispatcher, amb):
        ambiguities[0] = True


    f.add((object, object), identity, on_ambiguity=on_ambiguity)
    assert not ambiguities[0]
    f.add((object, float), identity, on_ambiguity=on_ambiguity)
    assert not ambiguities[0]
    f.add((float, object), identity, on_ambiguity=on_ambiguity)
    assert ambiguities[0]


def test_serializable():
    f = Dispatcher('f')
    f.add((int,), inc)
    f.add((float,), dec)
    f.add((object,), identity)

    import pickle
    assert isinstance(pickle.dumps(f), str)

    g = pickle.loads(pickle.dumps(f))

    assert g(1) == 2
    assert g(1.0) == 0.0
    assert g('hello') == 'hello'
