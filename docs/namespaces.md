Namespaces
==========

By default all dispatched methods share a common global namespace.  I.e. if two
imported modules implement a dispatched function with the same name then those
two functions are co-dispatched, even if the namespaces remain separate


Example
-------

```Python
# float_lib.py

@dispatch(float)
def f(x):
    print("Handles floats!")


# int_lib.py

@dispatch(int)
def f(x):
    print("Handles ints!")


# user_library.py

import float_lib
import int_lib

float_lib.f(1.0)  # Prints "Handles floats!" as expected
float_lib.f(1)    # Prints "Handles ints!" even though this if float_lib.f
                  # Because float_lib.f and int_lib.f both are in a globally
                  # dispatched namespace
```

Sometimes this is desired.  Sometimes it is not.  There are two strategies to
avoid unwanted conflicts

1. Appropriate naming
---------------------

1.  Dispatch mostly on types that you control
2.  Use descriptive names

Just like you wouldn't change the definition of `object.__str__` you probably
shouldn't define a function `f` on a type `int`.  This statement is too broad.
Instead, use specific names and limit yourself to your own types.

2. Use explicit namespaces
--------------------------

A dispatched namespace is nothing more than a dictionary mapping names of
functions (strings) to `Dispatcher` objects.

    namespace :: {str: Dispatcher}

The global namespace for `multipledispatch` lives in
`multipledispatch.global_namespace`.  If you prefer an isolated namespace you
can specify a new dictionary in the call to `dispatch`

```Python

my_namespace = dict()

@dispatch(int, namespace=my_namespace)
def f(x):
    print("Handles ints!")
```

This can be made more convenient with a quick call to `functools.partial`

```Python
from functools import partial

my_namespace = dict()
dispatch = partial(dispatch, namespace=my_namespace)

@dispatch(int)
def f(x):
    print("Handles ints!")
```
