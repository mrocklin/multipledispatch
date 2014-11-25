# This test module only checks for Python 2.x branches.
#
# For Python 3.x annotation unit tests, see the following file(s):
#  ./multipledispatch/tests/py3/test_annotations.py
import sys

from multipledispatch import core
from multipledispatch.utils import raises


def test_dispatch_on_annotations():
    if sys.version_info.major < 3:
        def f(x):
            return x

        assert raises(SyntaxError, lambda: core.dispatch_on_annotations(f))
