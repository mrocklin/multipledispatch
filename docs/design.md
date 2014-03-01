
Types
-----

    signature  :: [type] - a list of types

    Dispatcher :: {signature: func}
                  A mapping of type signatures to function implementations

    namespace  :: {str: Dispatcher}
                  A mapping from function names, like 'add' to Dispatchers

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
`Dispatcher`

```Python
def inc(x):
    return x + 1

def dec(x):
    return x - 1

f.add((int,), inc)  # f increments integers
f.add((float,), dec)  # f decrements floats

>>> f(1)
2

>>> f(1.0)
0.0
```

For notational convenience dispatcher's can use Python's decorator syntax to
register functions at definition time

```Python
f = Dispatcher('f')

@f.register(int)
def inc(x):
    return x + 1

@f.register(float)
def dec(x):
    return x - 1
```

    This is equivalent to the form above.


Namespaces and `dispatch`
-------------------------

The creation and manipulation of `Dispatcher` objects is hidden from the user
by the `dispatch` decorator.

```Python
@dispatch(int)
def f(x):
    return x + 1

@dispatch(float)
def f(x):
    return x - 1
```

The `dispatch` decorator uses the name of the function to select the
appropriate `Dispatcher` object to which it adds the new
signature/implementation.  Dispatch on a function with a never-before-seen name
creates and stores a new `Dispatcher` automatically.

```Python
# This creates and stores a new Dispatcher('g')
@dispatch(int)
def g(x):
    return x ** 2
```

This new `Dispatcher`s is stored a *namespace*, which is simply a dictionary
that maps function names like `'f'` to `Dispatcher` objects like
`Dispatcher('f')`.

By default `dispatch` uses the global namespace in
`multipledispatch.core.global_namespace`.  If used unwisely this global
namespace may cause conflicts and difficult to track down bugs.  Users who
desire additional security can establish their own namespaces simply by
creating a dictionary.

```Python
my_namespace = dict()

@dispatch(int, namespace=my_namespace)
def f(x):
    return x + 1
```

To establish a namespace for an entire project we suggest the use of
`functools.partial`

```Python
from functools import partial
from multipledispatch import dispatch

my_namespace = dict()
dispatch = partial(dispatch, namespace=my_namespace)

@dispatch(int)  # Uses my_namespace rather than global namespace
def f(x):
    return x + 1
```
