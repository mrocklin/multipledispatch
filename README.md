Multiple Dispatch
=================

[![](https://travis-ci.org/mrocklin/multipledispatch.png)](https://travis-ci.org/mrocklin/multipledispatch)


Arbitrary decisions
-------------------

We collect implementations based around the name of the function.  This
means that we ignore namespaces.

When the choice between two implementations is ambiguous then we choose one
pseudo-randomly and raise a warning.


What this does
--------------

*   Selects implementation from types of all non-keyword arguments

*   Supports inheritance

*   Supports union types `(int, float)`

*   Caches for fast repeated lookup

*   Performs static analysis at function definition time to identify possible
    ambiguities and provide suggestions to break those ambiguities


What this doesn't do
--------------------


*   Dispatch on class methods

    class Foo(object):
        @dispatch(int)
        def f(x):
            ...

*   Vararg dispatch

    @dispatch([int])
    def add(*args):
        ...

*   Diagonal dispatch

    a = arbitrary_type()
    @dispatch(a, a)
    def are_same_type(x, y):
        return True


Links
-----

*   [Five-minute Multimethods in Python by Guido](http://www.artima.com/weblogs/viewpost.jsp?thread=101605)
*   [`multimethods` package on PyPI](https://pypi.python.org/pypi/multimethods)
*   [Clojure Protocols](http://clojure.org/protocols)
*   [Julia methods docs](http://julia.readthedocs.org/en/latest/manual/methods/)
*   [Karpinksi notebook: *The Design Impact of Multiple Dispatch*](http://nbviewer.ipython.org/gist/StefanKarpinski/b8fe9dbb36c1427b9f22)
*   [Wikipedia article](http://en.wikipedia.org/wiki/Multiple_dispatch)
