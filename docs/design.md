
Types
-----

    signature  :: [type]
                  a list of types

    Dispatcher :: {signature: function}
                  A mapping of type signatures to function implementations

    namespace  :: {str: Dispatcher}
                  A mapping from function names, like 'add', to Dispatchers

Dispatchers
-----------

A `Dispatcher` object stores and selects between different implementations of
the same abstract operation.  It selects the appropriate implementation based
on a signature, or list of types.  We build one dispatcher per abstract
operation.

```Python
f = Dispatcher('f')
```

At the lowest level we build normal Python functions and then add them to the
`Dispatcher`.

```Python
def inc(x):
    return x + 1

def dec(x):
    return x - 1

f.add((int,), inc)    # f increments integers
f.add((float,), dec)  # f decrements floats

>>> f(1)
2

>>> f(1.0)
0.0
```

Internally `Dispatcher.resolve` selects the function implementation.

```Python
>>> f.resolve((int,))
<function __main__.inc>

>>> f.resolve((float,))
<function __main__.dec>
```

For notational convenience dispatchers leverage Python's decorator syntax to
register functions they we define them.

```Python
f = Dispatcher('f')

@f.register(int)
def inc(x):
    return x + 1

@f.register(float)
def dec(x):
    return x - 1
```

This is equivalent to the form above.  It also adheres to the standard
implemented by `functools.singledispatch` in Python 3.4.


Namespaces and `dispatch`
-------------------------

The the `dispatch` decorator hides the creation and manipulation of
`Dispatcher` objects from the user.

```Python
# f = Dispatcher('f')  # no need to create Dispatcher ahead of time

@dispatch(int)
def f(x):
    return x + 1

@dispatch(float)
def f(x):
    return x - 1
```

The `dispatch` decorator uses the name of the function to select the
appropriate `Dispatcher` object to which it adds the new
signature/function.  When it encounters a new function name it creates a new
`Dispatcher` object and stores it the name/Dispatcher pair in a namespace for
future reference.

```Python
# This creates and stores a new Dispatcher('g')
# namespace['g'] = Dispatcher('g')
@dispatch(int)
def g(x):
    return x ** 2
```

This new `Dispatcher` is stored a *namespace*, which is simply a dictionary
that maps function names like `'g'` to dispatcher objects like
`Dispatcher('g')`.

By default `dispatch` uses the global namespace in
`multipledispatch.core.global_namespace`.  If this global namespace is used
unwisely by several projects then conflicts may arise, causing difficult to
track down bugs.  Users who desire additional security can establish their own
namespaces simply by creating a dictionary.

```Python
my_namespace = dict()

@dispatch(int, namespace=my_namespace)
def f(x):
    return x + 1
```

To establish a namespace for an entire project we suggest the use of
`functools.partial` to bind your namespace to a new `dispatch` decorator.

```Python
from multipledispatch import dispatch
from functools import partial

my_namespace = dict()
dispatch = partial(dispatch, namespace=my_namespace)

@dispatch(int)  # Uses my_namespace rather than global namespace
def f(x):
    return x + 1
```
