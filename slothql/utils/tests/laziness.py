import pytest

from ..laziness import LazyInitMixin


class Executed(Exception):
    pass


class Class(LazyInitMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b
        raise Executed


def test_lazy_init_getattr():
    a = Class('foo', b='bar')
    with pytest.raises(Executed):
        hasattr(a, 'a')
    assert 'foo' is a.a
    assert 'bar' is a.b


def test_lazy_init_setattr():
    a = Class('foo', b='bar')
    with pytest.raises(Executed):
        a.c = 'not baz'  # isn't being fully executed, as an exception occurs first in __init__
    a.c = 'baz'
    assert 'foo' is a.a
    assert 'bar' is a.b
    assert 'baz' is a.c


def test_lazy_init_isinstance():
    assert isinstance(Class('foo', b='bar'), Class)
