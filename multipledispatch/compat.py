""" Compatibility module for Python 2 and Python 3

This module provides fully separable and thus testable functions which
codify some of the differences between Python 2 and Python 3 in the
multipledispatch library.
"""
import sys

from .dispatcher import MethodDispatcher


def get_method_dispatcher(name, frame, kwarg_dict, klass=MethodDispatcher):
    """ Required to support pypy 2.x

    The first branch below words for Python 2.x, 3.x, and pypy 3.x. However,
    it fails for pypy 2.x. This is the work-around.
    """
    if sys.version_info[0] >= 3:
        return get_f_locals_py3(kwarg_dict).get(name, klass(name))
    else:
        return get_f_locals_py2(frame).get(name, klass(name))


def get_f_locals_py2(frame):
    return frame.f_back.f_locals


def get_f_locals_py3(kwarg_dict):
    return kwarg_dict.get('frame', None).f_locals
