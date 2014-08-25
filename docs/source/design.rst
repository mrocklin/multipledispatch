Design
======

Types
-----

::

    signature  :: [type]
                  a list of types

    Dispatcher :: {signature: function}
                  A mapping of type signatures to function implementations

    namespace  :: {str: Dispatcher}
                  A mapping from function names, like 'add', to Dispatchers

Dispatchers
-----------

A ``Dispatcher`` object stores and selects between different
implementations of the same abstract operation. It selects the
appropriate implementation based on a signature, or list of types. We
build one dispatcher per abstract operation.

.. code::

    f = Dispatcher('f')

At the lowest level we build normal Python functions and then add them
to the ``Dispatcher``.

.. code::

    >>> def inc(x):
    ...     return x + 1

    >>> def dec(x):
    ...     return x - 1

    >>> f.add((int,), inc)    # f increments integers
    >>> f.add((float,), dec)  # f decrements floats

    >>> f(1)
    2

    >>> f(1.0)
    0.0

Internally ``Dispatcher.dispatch`` selects the function implementation.

.. code::

    >>> f.dispatch(int)
    <function __main__.inc>

    >>> f.dispatch(float)
    <function __main__.dec>

For notational convenience dispatchers leverage Python's decorator
syntax to register functions as we define them.

.. code::

    f = Dispatcher('f')

    @f.register(int)
    def inc(x):
        return x + 1

    @f.register(float)
    def dec(x):
        return x - 1

This is equivalent to the form above.
It adheres to the standard implemented by ``functools.singledispatch`` in
Python 3.4 (although the "functional form" of ``register`` is not supported).

As in ``singledispatch``, the ``register`` decorator returns the
undecorated function, which enables decorator stacking.

.. code::

    @f.register(str)
    @f.register(tuple)
    def rev(x):
        return x[::-1]


The Dispatcher creates a detailed docstring automatically.
To add a description of the multimethod itself,
provide it when creating the ``Dispatcher``.

.. code::

    >>> f = Dispatcher('f', doc="Do something to the argument")

    >>> @f.register(int)
    ... def inc(x):
    ...     "Integers are incremented"
    ...     return x + 1

    >>> @f.register(float)
    ... def dec(x):
    ...     "Floats are decremented"
    ...     return x - 1

    >>> @f.register(str)
    ... @f.register(tuple)
    ... def rev(x):
    ...     # no docstring
    ...     return x[::-1]

    >>> print(f.__doc__)
    Multiply dispatched method: f

    Do something to the argument

    Inputs: <float>
    ----------------
    Floats are decremented

    Inputs: <int>
    --------------
    Integers are incremented

    Other signatures:
        str
        tuple

Namespaces and ``dispatch``
---------------------------

The ``dispatch`` decorator hides the creation and manipulation of
``Dispatcher`` objects from the user.

.. code::

    # f = Dispatcher('f')  # no need to create Dispatcher ahead of time

    @dispatch(int)
    def f(x):
        return x + 1

    @dispatch(float)
    def f(x):
        return x - 1

The ``dispatch`` decorator uses the name of the function to select the
appropriate ``Dispatcher`` object to which it adds the new
signature/function. When it encounters a new function name it creates a
new ``Dispatcher`` object and stores name/Dispatcher pair in a namespace
for future reference.

.. code::

    # This creates and stores a new Dispatcher('g')
    # namespace['g'] = Dispatcher('g')
    # namespace['g'].add((int,), g)
    @dispatch(int)
    def g(x):
        return x ** 2

We store this new ``Dispatcher`` in a *namespace*. A namespace is simply
a dictionary that maps function names like ``'g'`` to dispatcher objects
like ``Dispatcher('g')``.

By default ``dispatch`` uses the global namespace in
``multipledispatch.core.global_namespace``. If several projects use this
global namespace unwisely then conflicts may arise, causing difficult to
track down bugs. Users who desire additional security may establish
their own namespaces simply by creating a dictionary.

.. code::

    my_namespace = dict()

    @dispatch(int, namespace=my_namespace)
    def f(x):
        return x + 1

To establish a namespace for an entire project we suggest the use of
``functools.partial`` to bind the new namespace to the ``dispatch``
decorator.

.. code::

    from multipledispatch import dispatch
    from functools import partial

    my_namespace = dict()
    dispatch = partial(dispatch, namespace=my_namespace)

    @dispatch(int)  # Uses my_namespace rather than the global namespace
    def f(x):
        return x + 1

