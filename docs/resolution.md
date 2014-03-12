Method Resolution
=================

Multiple dispatch selects the function from the types of the inputs.

```Python
@dispatch(int)
def f(x):           # increment integers
    return x + 1

@dispatch(float)
def f(x):           # decrement floats
    return x - 1

>>> f(1)            # 1 is an int, so increment
2
>>> f(1.0)          # 1.0 is a float, so decrement
0.0
```


Union Types
-----------

Similarly to `isinstance` you specify multiple valid types with a tuple.

```Python
@dispatch((list, tuple))
def f(x):
    """ Apply ``f`` to each element in a list or tuple """
    return [f(y) for y in x]

>>> f([1, 2, 3])
[2, 3, 4]

>>> f((1, 2, 3))
[2, 3, 4]
```

Abstract Types
--------------

You can also use abstract classes like `Iterable` and `Number` in place of
union types like `(list, tuple)` or `(int, float)`.

```Python
from collections import Iterable

# @dispatch((list, tuple))
@dispatch(Iterable)
def f(x):
    """ Apply ``f`` to each element in an Iterable """
    return [f(y) for y in x]
```


Selecting Specific Implementations
----------------------------------

If multiple valid implementations exist then we use the most specific one.  In
the following example we build a function to flatten nested iterables.

```Python
@dispatch(Iterable)
def flatten(L):
    return sum([flatten(x) for x in L], [])

@dispatch(object)
def flatten(x):
    return [x]

>>> flatten([1, 2, 3])
[1, 2, 3]

>>> flatten([1, [2], 3])
[1, 2, 3]

>>> flatten([1, 2, (3, 4), [[5]], [(6, 7), (8, 9)]])
[1, 2, 3, 4, 5, 6, 7, 8, 9]
```

Because strings are iterable they too will be flattened

```Python
>>> flatten([1, 'hello', 3])
[1, 'h', 'e', 'l', 'l', 'o', 3]
```

We avoid this by specializing `flatten` to `str`.  Because `str` is more
specific than `Iterable` this function takes precedence for strings.

```Python
@dispatch(str)
def flatten(s):
    return s

>>> flatten([1, 'hello', 3])
[1, 'hello', 3]
```

The `multipledispatch` project depends on Python's `issubclass` mechanism to
determine which types are more specific than others.


Multiple Inputs
---------------

All of these rules apply when we introduce multiple inputs.

```Python
@dispatch(object, object)
def f(x, y):
    return x + y

@dispatch(object, float)
def f(x, y):
    """ Square the right hand side if it is a float """
    return x + y**2

>>> f(1, 10)
11

>>> f(1.0, 10.0)
101.0
```


Ambiguities
-----------

However ambiguities arise when different implementations of a function are
equally valid

```Python
@dispatch(float, object)
def f(x, y):
    """ Square left hand side if it is a float """
    return x**2 + y

>>> f(2.0, 10.0)
?
```

Which result do we expect, `2.0**2 + 10.0` or `2.0 + 10.0**2`?  The types of
the inputs satisfy three different implementations, two of which have equal
validity

    input types:    float, float
    Option 1:       object, object
    Option 2:       object, float
    Option 3:       float, object

Option 1 is strictly less specific than either options 2 or 3 so we discard
it.  Options 2 and 3 however are equally specific and so it is unclear which
to use.

To resolve issues like this `multipledispatch` inspects the type signatures
given to it and searches for ambiguities.  It then raises a warning like the
following:

```
multipledispatch/dispatcher.py:74: AmbiguityWarning:
Ambiguities exist in dispatched function f

The following signatures may result in ambiguous behavior:
    [object, float], [float, object]


Consider making the following additions:

@dispatch(float, float)
def f(...)
```

This warning occurs when you write the function and guides you to create an
implementation to break the ambiguity.  In tihs case, a function with signature
`(float, float)` is more specific than either options 2 or 3 and so resolves
the issue.  To avoid this warning you should implement this new function
*before* the others.

```Python
@dispatch(float, float)
def f(x, y):
    ...

@dispatch(float, object)
def f(x, y):
    ...

@dispatch(object, float)
def f(x, y):
    ...
```

If you do not resolve ambiguities by creating more specific functions then one
of the competing functions will be selected pseudo-randomly.
