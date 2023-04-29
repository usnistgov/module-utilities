from __future__ import annotations
import pytest


from module_utilities import cached


class Baseclass:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get_value(self):
        return self.a, self.b

    def get_xy(self, x, y):
        return self.get_value() + (x, y)


def prop_test(obj, prop, value, key=None, docstring=None):
    """test a single property"""
    if key is None:
        key = prop

    assert getattr(obj, prop) == value
    # test coming from cache
    assert getattr(obj, prop) is obj._cache[key]
    # test is same
    assert getattr(obj, prop) is getattr(obj, prop)

    if docstring is not None:
        assert getattr(type(obj), prop).__doc__ == docstring


def meth_test(obj, meth, value, args=None, kws=None, key=None, docstring=None):
    """test a single property"""

    if args is None:
        args = ()
    if kws is None:
        kws = {}

    if key is None:
        key = meth

    assert getattr(obj, meth)(*args, **kws) == value
    # test coming from cache
    assert getattr(obj, meth)(*args, **kws) is obj._cache[key]
    # test is same
    assert getattr(obj, meth)(*args, **kws) is getattr(obj, meth)(*args, **kws)

    if docstring is not None:
        assert getattr(type(obj), meth).__doc__ == docstring


def do_prop_test(x, key=None, docstring="a doc string", check_empty=True):
    if key is None:
        key = "prop"

    # nothing here
    if check_empty:
        assert not hasattr(x, "_cache") or len(x._cache) == 0
    prop_test(x, prop="prop", value=(1, 2), key=key, docstring=docstring)

    assert tuple(x._cache.keys()) == (key,)

    # change value
    x.a, x.b = 2, 4

    prop_test(x, prop="prop", value=(1, 2), key=key, docstring=docstring)

    # remove cache:
    del x._cache
    prop_test(x, prop="prop", value=(2, 4), key=key, docstring=docstring)


def test_prop():
    class test(Baseclass):
        @cached.prop
        def prop(self):
            "a doc string"
            return self.get_value()

    do_prop_test(test(1, 2))

    class test(Baseclass):
        @cached.prop()
        def prop(self):
            "a doc string"
            self._hello = 1
            return self.get_value()

    do_prop_test(test(1, 2))

    class test(Baseclass):
        @cached.prop(key="there")
        def prop(self):
            "a doc string"
            return self.get_value()

    do_prop_test(test(1, 2), key="there")

    class test(Baseclass):
        @cached.decorate()
        def prop(self):
            "a doc string"
            self._hello = 1
            return self.get_value()

    do_prop_test(test(1, 2))

    class test(Baseclass):
        @cached.decorate(key="there")
        def prop(self):
            "a doc string"
            return self.get_value()

    do_prop_test(test(1, 2), key="there")


def do_meth_test(x, key=None, docstring="a doc string", check_empty=True):
    if key is None:
        key = "meth"

    key_tot = (key, (3, 4), frozenset())

    target = (1, 2, 3, 4)
    if check_empty:
        assert not hasattr(x, "_cache") or len(x._cache) == 0
    meth_test(x, "meth", target, args=(3, 4), key=key_tot, docstring=docstring)

    assert tuple(x._cache.keys()) == (key_tot,)

    # change value
    x.a = 2
    x.b = 4

    meth_test(x, "meth", target, args=(3, 4), key=key_tot, docstring=docstring)
    assert tuple(x._cache.keys()) == (key_tot,)

    # remove cache:
    del x._cache
    target = (2, 4, 3, 4)
    meth_test(x, "meth", target, args=(3, 4), key=key_tot, docstring=docstring)
    assert tuple(x._cache.keys()) == (key_tot,)

    # getting write signature
    del x._cache
    meth_test(x, "meth", target, kws=dict(x=3, y=4), key=key_tot, docstring=docstring)
    assert tuple(x._cache.keys()) == (key_tot,)

    del x._cache
    meth_test(x, "meth", target, kws=dict(y=4, x=3), key=key_tot, docstring=docstring)
    assert tuple(x._cache.keys()) == (key_tot,)

    del x._cache
    meth_test(
        x, "meth", target, args=(3,), kws=dict(y=4), key=key_tot, docstring=docstring
    )
    assert tuple(x._cache.keys()) == (key_tot,)


def test_meth():
    class test(Baseclass):
        @cached.decorate(as_property=False)
        def meth(self, x, y):
            "a doc string"
            return self.get_xy(x, y)

    do_meth_test(test(1, 2))

    class test(Baseclass):
        @cached.meth
        def meth(self, x, y):
            "a doc string"
            return self.get_xy(x, y)

    do_meth_test(test(1, 2))

    class test(Baseclass):
        @cached.meth()
        def meth(self, x, y):
            "a doc string"
            return self.get_xy(x, y)

    do_meth_test(test(1, 2))

    class test(Baseclass):
        @cached.meth(key="there")
        def meth(self, x, y):
            "a doc string"
            return self.get_xy(x, y)

    do_meth_test(test(1, 2), key="there")


def test_clear():
    class test(Baseclass):
        def __init__(self, a, b):
            self._a = a
            self._b = b

        @property
        def a(self):
            return self._a

        @a.setter
        @cached.clear
        def a(self, val):
            self._a = val

        @property
        def b(self):
            return self._b

        @b.setter
        @cached.clear
        def b(self, val):
            self._b = val

        @cached.clear
        def clear_all(self):
            "a clear string"
            pass

        @property
        def aprop(self):
            return self._aprop

        @cached.prop
        def test_prop(self):
            return [2.0]

        @aprop.setter
        @cached.clear("prop", "test_prop")
        def aprop(self, val):
            self._aprop = val

        @cached.prop
        def prop(self):
            "a doc string"
            return self.get_value()

        @cached.clear("meth")
        def clear_meth(self):
            pass

        @cached.meth
        def meth(self, x, y):
            "a doc string"
            return self.get_xy(x, y)

    x = test(1, 2)
    key_prop = "prop"
    key_meth = ("meth", (3, 4), frozenset())
    docstring = "a doc string"
    prop_test(x, prop="prop", value=(1, 2), key=key_prop, docstring=docstring)
    meth_test(
        x,
        meth="meth",
        value=(1, 2, 3, 4),
        args=(3, 4),
        key=key_meth,
        docstring=docstring,
    )

    # this clears the cache
    x.a, x.b = 2, 4
    key_meth = ("meth", (3, 4), frozenset())
    docstring = "a doc string"
    prop_test(x, prop="prop", value=(2, 4), key=key_prop, docstring=docstring)
    meth_test(
        x,
        meth="meth",
        value=(2, 4, 3, 4),
        args=(3, 4),
        key=key_meth,
        docstring=docstring,
    )

    assert type(x).clear_all.__doc__ == "a clear string"

    x.clear_all()
    assert len(x._cache) == 0

    x.prop
    x.meth(3, 4)

    assert key_prop in x._cache
    assert key_meth in x._cache

    x.test_prop
    assert "test_prop" in x._cache
    x.aprop = 2
    assert key_prop not in x._cache
    assert "test_prop" not in x._cache
    assert key_meth in x._cache

    x.prop
    x.meth(3, 4)
    x.meth(5, 6)
    key_meth2 = ("meth", (5, 6), frozenset())

    assert key_prop in x._cache
    assert key_meth in x._cache
    assert key_meth2 in x._cache

    x.clear_meth()
    assert key_meth not in x._cache
    assert key_meth2 not in x._cache
    assert key_prop in x._cache


def test_use_cache():
    class tmp:
        _use_cache = False

        @cached.prop(check_use_cache=True)
        def prop0(self):
            return [1, 2]

        @cached.prop
        def prop1(self):
            return [2, 3]

        @cached.decorate(check_use_cache=True)
        def prop2(self):
            return [1, 2]

        @cached.decorate()
        def prop3(self):
            return [1, 2]

    x = tmp()

    for p in ["prop0", "prop2"]:
        assert getattr(x, p) is not getattr(x, p)
        assert not hasattr(x, "_cache") or p not in x._cache

    for p in ["prop1", "prop3"]:
        assert getattr(x, p) is getattr(x, p)
        assert p in x._cache

    class tmp:
        _use_cache = True

        @cached.prop(check_use_cache=True)
        def prop0(self):
            return [1, 2]

        @cached.prop
        def prop1(self):
            return [2, 3]

        @cached.decorate(check_use_cache=True)
        def prop2(self):
            return [1, 2]

        @cached.decorate()
        def prop3(self):
            return [1, 2]

    x = tmp()

    for p in ["prop0", "prop1", "prop2", "prop3"]:
        assert getattr(x, p) is getattr(x, p)
        assert p in x._cache

    # if not have _use_cache parameter
    class tmp:
        @cached.prop(check_use_cache=True)
        def prop0(self):
            return [1, 2]

        @cached.prop
        def prop1(self):
            return [2, 3]

        @cached.decorate(check_use_cache=True)
        def prop2(self):
            return [1, 2]

        @cached.decorate()
        def prop3(self):
            return [1, 2]

    x = tmp()

    for p in ["prop0", "prop2"]:
        assert getattr(x, p) is not getattr(x, p)
        assert not hasattr(x, "_cache") or p not in x._cache

    for p in ["prop1", "prop3"]:
        assert getattr(x, p) is getattr(x, p)
        assert p in x._cache


def test_error_with_slots():
    class test:
        __slots__ = ["a", "b"]

        def __init__(self, a, b):
            self.a = a
            self.b = b

        @cached.prop
        def prop(self):
            return self.a, self.b

    x = test(1, 2)

    with pytest.raises(AttributeError):
        x.prop

    class test:
        __slots__ = ["a", "b", "_cache"]

        def __init__(self, a, b):
            self.a = a
            self.b = b

        @cached.prop
        def prop(self):
            "a doc string"
            return self.a, self.b

    x = test(1, 2)
    do_prop_test(x)


def test_typing():
    class Example:
        @cached.prop
        def aprop(self) -> list[float]:
            return [1.0, 2.0]

        @cached.meth
        def ameth(self, a: float = 1.0, b: float = 2.0) -> list[float]:
            return [a, b]

    x = Example()
    assert x.aprop == [1.0, 2.0]
    assert x.ameth(2.0, 3.0) == [2.0, 3.0]
