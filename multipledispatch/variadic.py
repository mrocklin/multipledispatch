import six

from .utils import typename


class VariadicSignatureType(type):
    # checking if subclass is a subclass of self
    def __subclasscheck__(self, subclass):
        other_type = getattr(subclass, 'value_type', (subclass,))
        return subclass is self or all(
            issubclass(other, self.value_type) for other in other_type
        )


def isvariadic(obj):
    """Check whether the type `obj` is variadic.

    Parameters
    ----------
    obj : type
        The type to check

    Returns
    -------
    bool
        Whether or not `obj` is variadic

    Examples
    --------
    >>> isvariadic(int)
    False
    >>> isvariadic(Variadic[int])
    True
    """
    return isinstance(obj, VariadicSignatureType)


class VariadicSignatureMeta(type):
    """A metaclass that overrides ``__getitem__`` on the class. This is used to
    generate a new type for Variadic signatures. See the Variadic class for
    examples of how this behaves.
    """
    def __getitem__(self, value_type):
        assert isinstance(value_type, (type, tuple)), type(value_type)
        if not isinstance(value_type, tuple):
            value_type = value_type,
        return VariadicSignatureType(
            'Variadic[%s]' % typename(value_type),
            (),
            dict(value_type=value_type, __slots__=())
        )


class Variadic(six.with_metaclass(VariadicSignatureMeta)):
    """A class whose getitem method can be used to generate a new type
    representing a specific variadic signature.

    Examples
    --------
    >>> Variadic[int]  # any number of int arguments
    <class 'multipledispatch.variadic.Variadic[int]'>
    >>> Variadic[(int, str)]  # any number of one of int or str arguments
    <class 'multipledispatch.variadic.Variadic[(int, str)]'>
    >>> issubclass(int, Variadic[int])
    True
    >>> issubclass(int, Variadic[(int, str)])
    True
    >>> issubclass(str, Variadic[(int, str)])
    True
    >>> issubclass(float, Variadic[(int, str)])
    False
    """
