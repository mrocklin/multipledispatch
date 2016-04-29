Multiple Dispatch 2
=================

|Build Status| |Coverage Status| |Version Status| |Downloads|

This is a fork from `mroklin's multipledispatch<https://github.com/mrocklin/multipledispatch>`_, which is designed to fully support python 3's type annotation.

And it only supports python 3.3+.

Example
-------

.. code-block:: python

   >>> from multipledispatch2 import dispatch

   >>> @dispatch
   ... def add(x: int, y: int) -> int:
   ...     return x + y

   >>> @dispatch
   ... def add(x, y):
   ...     return "%s + %s" % (x, y)

   >>> add(1, 2)
   3

   >>> add(1, 'hello')
   '1 + hello'

What this does
--------------

-  Dispatches on all non-keyword arguments

-  Supports inheritance

-  Supports instance methods

-  Supports union types, e.g. ``(int, float)``

-  Supports builtin abstract classes, e.g. ``Iterator, Number, ...``

-  Caches for fast repeated lookup

-  Identifies possible ambiguities at function definition time

-  Provides hints to resolve ambiguities when they occur

-  Supports namespaces with optional keyword arguments

What this doesn't do
--------------------

-  Vararg dispatch

.. code-block:: python

   import typing

   @dispatch
   def add(*args: typing.Iterable[int]):
       ...

-  Diagonal dispatch

.. code-block:: python

   a = arbitrary_type()
   @dispatch
   def are_same_type(x: a, y: a) -> bool:
       return True

-  Efficient update: The addition of a new signature requires a full resolve of
   the whole function.  This becomes troublesome after you get to a few hundred
   type signatures.  It can be mitigated by halting and restarting ordering see
   (``halt_ordering`` and ``restart_ordering`` functions for more information.)


Installation and Dependencies
-----------------------------

``multipledispatch2`` is on the Python Package Index (PyPI):

::

    pip install multipledispatch2

or

::

    easy_install multipledispatch2


``multipledispatch2`` is only supports Python 3.3+.  It is pure Python and requires no dependencies beyond the standard
library.

It is, in short, a light weight dependency.


License
-------

New BSD. See License_.


Links
-----

-  `Five-minute Multimethods in Python by Guido`_
-  `multimethods package on PyPI`_
-  `singledispatch in Python 3.4's functools`_
-  `Clojure Protocols`_
-  `Julia methods docs`_
-  `Karpinksi notebook: *The Design Impact of Multiple Dispatch*`_
-  `Wikipedia article`_
-  `PEP 3124 - *Overloading, Generic Functions, Interfaces, and Adaptation*`_
-  `PEP 0484 - *Type Hints*`_

.. _`Five-minute Multimethods in Python by Guido`:
  http://www.artima.com/weblogs/viewpost.jsp?thread=101605
.. _`multimethods package on PyPI`:
  https://pypi.python.org/pypi/multimethods
.. _`singledispatch in Python 3.4's functools`:
  http://docs.python.org/3.4/library/functools.html#functools.singledispatch
.. _`Clojure Protocols`:
  http://clojure.org/protocols
.. _`Julia methods docs`:
  http://julia.readthedocs.org/en/latest/manual/methods/
.. _`Karpinksi notebook: *The Design Impact of Multiple Dispatch*`:
  http://nbviewer.ipython.org/gist/StefanKarpinski/b8fe9dbb36c1427b9f22
.. _`Wikipedia article`:
  http://en.wikipedia.org/wiki/Multiple_dispatch
.. _`PEP 3124 - *Overloading, Generic Functions, Interfaces, and Adaptation*`:
  http://legacy.python.org/dev/peps/pep-3124/
.. _`PEP 0484 - *Type Hints*`:
  https://www.python.org/dev/peps/pep-0484/

.. |Build Status| image:: https://travis-ci.org/mrocklin/multipledispatch.png
   :target: https://travis-ci.org/mrocklin/multipledispatch
.. |Version Status| image:: https://pypip.in/v/multipledispatch/badge.png
   :target: https://pypi.python.org/pypi/multipledispatch/
.. |Downloads| image:: https://pypip.in/d/multipledispatch/badge.png
   :target: https://pypi.python.org/pypi/multipledispatch/
.. |Coverage Status| image:: https://coveralls.io/repos/mrocklin/multipledispatch/badge.png
   :target: https://coveralls.io/r/mrocklin/multipledispatch
.. _License: https://github.com/mrocklin/multipledispatch/blob/master/LICENSE.txt

