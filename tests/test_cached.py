# mypy: disable-error-code="no-untyped-def, no-untyped-call"

from __future__ import annotations

from typing import Any

import pytest

from module_utilities import cached


def test_cachedproperty() -> None:
    class Tmp:
        def __init__(self) -> None:
            self._cache: dict[str, Any] = {}

        @cached.CachedProperty
        def thing(self) -> int:
            """A test"""
            return 1

        @cached.prop
        def there(self) -> int:
            """B test"""
            return 2

    x = Tmp()
    assert x.thing == 1

    assert x._cache == {"thing": 1}
    assert Tmp.there.__name__ == "there"
    assert Tmp.there.__doc__ == "B test"

    with pytest.raises(AttributeError):
        x.thing = 2


# NOTE: specifically testing class without _cache defined
# so need ignores
def test_cachedproperty_without_cache() -> None:
    class Tmp:
        @cached.CachedProperty  # type: ignore[type-var]
        def thing(self) -> int:
            """A test"""
            return 1

        @cached.prop  # type: ignore[type-var]
        def there(self) -> int:
            """B test"""
            return 2

        @cached.clear  # type: ignore[type-var]
        def clear(self) -> None:
            pass

    x = Tmp()

    assert not hasattr(x, "_cache")
    x.clear()

    assert x.thing == 1

    assert x._cache == {"thing": 1}  # type: ignore[attr-defined]
    assert Tmp.there.__name__ == "there"
    assert Tmp.there.__doc__ == "B test"

    with pytest.raises(AttributeError):
        x.thing = 2

    x.clear()
    assert x._cache == {}  # type: ignore[attr-defined]


def test_meth_bad_hash() -> None:
    # test that passing unhashable just returns the func
    class Tmp:
        def __init__(self) -> None:
            self._cache: dict[str, Any] = {}

        @cached.meth
        def thing(self, x: Any) -> Any:
            return x

    x = Tmp()

    assert x.thing(1) == 1

    assert "thing" in x._cache

    x._cache = {}
    v = {"a": 1}
    assert x.thing(v) == v
    assert len(x._cache["thing"]) == 0


class Baseclass:
    def __init__(self, a, b) -> None:
        self.a = a
        self.b = b
        self._cache: dict[str, Any] = {}

    def get_value(self) -> tuple[Any, ...]:
        return self.a, self.b

    def get_xy(self, x, y) -> tuple[Any, ...]:
        return (*self.get_value(), x, y)


def prop_test(obj, prop, value, key=None, docstring=None) -> None:
    """Test a single property"""
    if key is None:
        key = prop

    assert getattr(obj, prop) == value
    # test coming from cache
    assert getattr(obj, prop) is obj._cache[key]
    # test is same
    assert getattr(obj, prop) is getattr(obj, prop)

    if docstring is not None:
        assert getattr(type(obj), prop).__doc__ == docstring


def meth_test(obj, meth, value, args=None, kws=None, key=None, docstring=None) -> None:
    """Test a single property"""

    if args is None:
        args = ()
    if kws is None:
        kws = {}

    param = None
    if key is None:
        key = meth
    elif isinstance(key, tuple):
        key, param = key

    assert getattr(obj, meth)(*args, **kws) == value
    # test coming from cache

    if param is None:
        assert getattr(obj, meth)(*args, **kws) is obj._cache[key]
    else:
        assert getattr(obj, meth)(*args, **kws) is obj._cache[key][param]

    # test is same
    assert getattr(obj, meth)(*args, **kws) is getattr(obj, meth)(*args, **kws)

    if docstring is not None:
        assert getattr(type(obj), meth).__doc__ == docstring


def do_prop_test(x, key=None, docstring="A doc string", check_empty=True) -> None:
    if key is None:
        key = "prop"

    # nothing here
    if check_empty:
        assert not hasattr(x, "_cache") or len(x._cache) == 0
    prop_test(x, prop="prop", value=(1, 2), key=key, docstring=docstring)

    assert tuple(x._cache.keys()) == (key,)  # pytype: disable=attribute-error

    # change value
    x.a, x.b = 2, 4

    prop_test(x, prop="prop", value=(1, 2), key=key, docstring=docstring)

    # remove cache:
    del x._cache
    prop_test(x, prop="prop", value=(2, 4), key=key, docstring=docstring)


def test_prop() -> None:
    class test(Baseclass):
        @cached.prop
        def prop(self):
            """A doc string"""
            return self.get_value()

    do_prop_test(test(1, 2))


def test_prop2() -> None:
    class test(Baseclass):
        @cached.prop()
        def prop(self):
            """A doc string"""
            self._hello = 1
            return self.get_value()

    do_prop_test(test(1, 2))


def test_prop3() -> None:
    class test(Baseclass):
        @cached.prop(key="there")
        def prop(self):
            """A doc string"""
            return self.get_value()

    do_prop_test(test(1, 2), key="there")


def test_prop4() -> None:
    class test(Baseclass):
        @cached.decorate()
        def prop(self):
            """A doc string"""
            self._hello = 1
            return self.get_value()

    do_prop_test(test(1, 2))


def test_prop5() -> None:
    class test(Baseclass):
        @cached.decorate(key="there")
        def prop(self):
            """A doc string"""
            return self.get_value()

    do_prop_test(test(1, 2), key="there")


def do_meth_test(x, key=None, docstring="A doc string", check_empty=True) -> None:
    if key is None:
        key = "meth"

    key_param: tuple[tuple[Any, ...], frozenset[Any]] = ((3, 4), frozenset())

    key_tot = (key, key_param)

    def test_keys(x) -> None:
        assert tuple(x._cache.keys()) == (key,)
        assert tuple(x._cache[key].keys()) == (key_param,)

    target = (1, 2, 3, 4)
    if check_empty:
        assert not hasattr(x, "_cache") or len(x._cache) == 0
    meth_test(x, "meth", target, args=(3, 4), key=key_tot, docstring=docstring)
    test_keys(x)

    # change value
    x.a = 2
    x.b = 4

    meth_test(x, "meth", target, args=(3, 4), key=key_tot, docstring=docstring)
    test_keys(x)

    # remove cache:
    del x._cache
    target = (2, 4, 3, 4)
    meth_test(x, "meth", target, args=(3, 4), key=key_tot, docstring=docstring)
    test_keys(x)

    # getting write signature
    del x._cache
    meth_test(x, "meth", target, kws={"x": 3, "y": 4}, key=key_tot, docstring=docstring)
    test_keys(x)

    del x._cache
    meth_test(x, "meth", target, kws={"y": 4, "x": 3}, key=key_tot, docstring=docstring)
    test_keys(x)

    del x._cache
    meth_test(
        x, "meth", target, args=(3,), kws={"y": 4}, key=key_tot, docstring=docstring
    )
    test_keys(x)


def test_meth() -> None:
    class test(Baseclass):
        @cached.decorate(as_property=False)
        def meth(self, x, y):
            """A doc string"""
            return self.get_xy(x, y)

    do_meth_test(test(1, 2))


def test_meth2() -> None:
    class test(Baseclass):
        @cached.meth
        def meth(self, x, y):
            """A doc string"""
            return self.get_xy(x, y)

    do_meth_test(test(1, 2))


def test_meth3() -> None:
    class test(Baseclass):
        @cached.meth()
        def meth(self, x, y):
            """A doc string"""
            return self.get_xy(x, y)

    do_meth_test(test(1, 2))


def test_meth4() -> None:
    class test(Baseclass):
        @cached.meth(key="there")
        def meth(self, x, y):
            """A doc string"""
            return self.get_xy(x, y)

    do_meth_test(test(1, 2), key="there")


def test_clear() -> None:  # noqa: C901
    class test(Baseclass):
        def __init__(self, a, b) -> None:
            self._a = a
            self._b = b

            self._cache = {}

        @property
        def a(self):
            return self._a

        @a.setter
        @cached.clear
        def a(self, val) -> None:
            self._a = val

        @property
        def b(self):
            return self._b

        @b.setter
        @cached.clear
        def b(self, val) -> None:
            self._b = val

        @cached.clear
        def clear_all(self) -> None:
            """A clear string"""

        @property
        def aprop(self):
            if hasattr(self, "_aprop"):
                return self._aprop
            msg = "must set aprop"
            raise ValueError(msg)

        @aprop.setter
        @cached.clear("prop", "test_prop")
        def aprop(self, val) -> None:
            self._aprop = val

        @cached.prop
        def test_prop(self):
            return [2.0]

        @cached.prop
        def prop(self):
            """A doc string"""
            return self.get_value()

        @cached.clear("meth")
        def clear_meth(self) -> None:
            pass

        @cached.meth
        def meth(self, x, y):
            """A doc string"""
            return self.get_xy(x, y)

        # check that clearing unknown key is fine
        @cached.clear("a_meth_that_isnt_there")
        def clear_missing(self) -> None:
            pass

    x = test(1, 2)
    key_prop = "prop"
    key_meth = ("meth", ((3, 4), frozenset()))  # type: ignore[var-annotated]
    docstring = "A doc string"
    prop_test(x, prop="prop", value=(1, 2), key=key_prop, docstring=docstring)
    meth_test(
        x,
        meth="meth",
        value=(1, 2, 3, 4),
        args=(3, 4),
        key=key_meth,
        docstring=docstring,
    )

    keys0 = list(x._cache.keys())

    x.clear_missing()

    assert list(x._cache.keys()) == keys0

    # this clears the cache
    x.a, x.b = 2, 4
    key_meth = ("meth", ((3, 4), frozenset()))
    docstring = "A doc string"
    prop_test(x, prop="prop", value=(2, 4), key=key_prop, docstring=docstring)
    meth_test(
        x,
        meth="meth",
        value=(2, 4, 3, 4),
        args=(3, 4),
        key=key_meth,
        docstring=docstring,
    )

    assert type(x).clear_all.__doc__ == "A clear string"

    x.clear_all()
    assert len(x._cache) == 0

    _ = x.prop
    x.meth(3, 4)

    def _test_key_meth(key_meth, x) -> None:
        assert key_meth[0] in x._cache
        assert key_meth[1] in x._cache[key_meth[0]]

    assert key_prop in x._cache
    _test_key_meth(key_meth, x)

    _ = x.test_prop
    assert "test_prop" in x._cache
    x.aprop = 2
    assert key_prop not in x._cache
    assert "test_prop" not in x._cache
    _test_key_meth(key_meth, x)

    _ = x.prop
    x.meth(3, 4)
    x.meth(5, 6)
    key_meth2 = ("meth", ((5, 6), frozenset()))  # type: ignore[var-annotated]

    assert key_prop in x._cache
    _test_key_meth(key_meth, x)
    _test_key_meth(key_meth2, x)

    x.clear_meth()
    assert key_meth[0] not in x._cache
    assert key_meth2[0] not in x._cache
    assert key_prop in x._cache


def test_use_cache() -> None:
    class Tmp:
        _use_cache = False

        def __init__(self) -> None:
            self._cache: dict[str, Any] = {}

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

        @cached.meth
        def meth0(self):
            return [1, 2]

        @cached.meth(check_use_cache=True)
        def meth1(self):
            return [1, 2]

    x = Tmp()

    for p in ["prop0", "prop2"]:
        assert getattr(x, p) is not getattr(x, p)
        assert not hasattr(x, "_cache") or p not in x._cache

    for p in ["prop1", "prop3"]:
        assert getattr(x, p) is getattr(x, p)
        assert p in x._cache

    assert x.meth0() is x.meth0()
    assert x.meth1() is not x.meth1()

    assert "meth0" in x._cache
    assert "meth1" not in x._cache


def test_use_cache2() -> None:  # noqa: C901
    class Tmp:
        _use_cache = True

        def __init__(self) -> None:
            self._cache: dict[str, Any] = {}

        @cached.prop(check_use_cache=True)
        def prop0(self):
            return [1, 2]

        @cached.prop
        def prop1(self):
            return [2, 3]

        @cached.decorate(check_use_cache=True, key="prop2")
        def prop2(self) -> list[int]:
            return [1, 2]

        @cached.decorate()
        def prop3(self) -> list[int]:
            return [1, 2]

        @cached.decorate(check_use_cache=True, as_property=False)
        def meth(self) -> list[int]:
            return [1, 2, 3]

        @cached.meth
        def meth1(self) -> list[int]:
            return [1, 2, 3]

        @cached.meth(key="a thing")
        def meth2(self, a: int) -> list[int]:
            return [a, *self.prop3]

        @cached.decorate(key="there", as_property=False)
        def there(self) -> list[int]:
            return [1, 2]

        @cached.decorate(key="something")
        def prop4(self) -> list[int]:
            return [1, 2]

        @property
        @cached.clear
        def prop_test(self) -> list[int]:
            return [1, 2]

        @cached.clear("meth1")
        def clearer(self) -> list[int]:
            return [1, 2]

        clearer = cached.clear(clearer, "meth2")

    x = Tmp()

    for p in ["prop0", "prop1", "prop2", "prop3"]:
        assert getattr(x, p) is getattr(x, p)
        assert p in x._cache


def test_use_cache3() -> None:
    # if not have _use_cache parameter
    class Tmp:
        def __init__(self) -> None:
            self._cache: dict[str, Any] = {}

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

    x = Tmp()

    for p in ["prop0", "prop2"]:
        assert getattr(x, p) is not getattr(x, p)
        assert not hasattr(x, "_cache") or p not in x._cache

    for p in ["prop1", "prop3"]:
        assert getattr(x, p) is getattr(x, p)
        assert p in x._cache


def test_error_with_slots() -> None:
    # ignore type errors here
    # the point is to make sure errors happen here.
    class test:
        __slots__ = ["a", "b"]

        def __init__(self, a, b) -> None:
            self.a = a
            self.b = b

        @cached.prop  # type: ignore[type-var]
        def prop(self):
            return self.a, self.b

    x = test(1, 2)

    with pytest.raises(AttributeError):
        _ = x.prop

    # but this should work fine:
    class test2:
        __slots__ = ["_cache", "a", "b"]

        def __init__(self, a, b) -> None:
            self.a = a
            self.b = b
            self._cache: dict[str, Any] = {}

        @cached.prop
        def prop(self):
            return self.a, self.b

    x2 = test2(1, 2)

    assert x2.prop == (1, 2)
    assert x2._cache["prop"] == (1, 2)


def test_error_with_slots2() -> None:
    class test:
        __slots__ = ["_cache", "a", "b"]

        def __init__(self, a, b) -> None:
            self.a = a
            self.b = b
            self._cache: dict[str, Any] = {}

        @cached.prop
        def prop(self):
            """A doc string"""
            return self.a, self.b

    x = test(1, 2)
    do_prop_test(x)


def test_with_kwargs() -> None:
    class test:
        def __init__(self) -> None:
            self._cache: dict[str, Any] = {}

        @cached.prop
        def prop(self) -> float:
            return 1.0

        @cached.meth
        def meth0(self, beta: float) -> float:
            return beta

        @cached.meth
        def meth1(self, *args: int) -> tuple[int, ...]:
            return args

        @cached.meth
        def meth2(self, /, **kws: int) -> dict[str, int]:
            return kws

        @cached.meth
        def meth3(
            self, /, *args: int, **kwargs: int
        ) -> tuple[tuple[int, ...], dict[str, int]]:
            return args, kwargs

        @cached.meth
        def meth4(self, beta: float, *args: int) -> tuple[float, tuple[int, ...]]:
            return beta, args

        # either of these will work.
        @cached.meth
        def meth5(
            self, beta: float, /, *args: int, **kwargs: int
        ) -> tuple[float, tuple[int, ...], dict[str, int]]:
            return beta, args, kwargs

        @cached.meth
        def meth5b(
            self, /, beta: float, *args: int, **kwargs: int
        ) -> tuple[float, tuple[int, ...], dict[str, int]]:
            return beta, args, kwargs

    test()


def test_meth_single_arg() -> None:
    class Tmp:
        _use_cache = False

        def __init__(self) -> None:
            self._cache: dict[str, Any] = {}

        @cached.meth
        def meth(self) -> float:
            return 1.0

        @property
        @cached.meth
        def prop(self) -> int:
            return 1

        @property
        @cached.meth(check_use_cache=True)
        def prop_check(self) -> int:
            return 2

        @cached.meth(check_use_cache=True)
        def meth_check(self, x: float) -> float:
            return x

    x = Tmp()

    assert x.meth() == 1.0
    assert x.prop == 1
    assert x.prop_check == 2
    assert x.meth_check(2.0) == 2.0

    assert x._cache["meth"] is x.meth()
    assert x._cache["prop"] is x.prop

    assert "prop_check" not in x._cache
    assert "meth_check" not in x._cache
