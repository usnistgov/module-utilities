# pyright: reportPrivateUsage=false

from __future__ import annotations

import dataclasses
from typing import Any

import attrs

from module_utilities import cached


def test_attrs_class() -> None:
    @attrs.define
    class Example:
        _cache: dict[str, Any] = attrs.field(factory=dict, init=False)  # pyright: ignore[reportUnknownVariableType]

        @cached.prop
        def prop(self) -> int:
            return 1

        @cached.meth
        def meth_0(self) -> int:
            return 1

        @cached.meth
        def meth_1(self, x: float) -> float:
            return x * 2

        @cached.clear("meth_0", "meth_1")
        def clear(self) -> None:
            pass

    x = Example()

    assert x._cache == {}
    assert x.prop == 1
    assert x.meth_0() == 1
    assert x.meth_1(2.0) == 4.0

    for key in ["prop", "meth_0", "meth_1"]:
        assert key in x._cache

    x.clear()
    assert list(x._cache.keys()) == ["prop"]


def test_attrs_class_frozen() -> None:
    import attrs

    @attrs.frozen
    class Example:
        _cache: dict[str, Any] = attrs.field(factory=dict, init=False)  # pyright: ignore[reportUnknownVariableType]

        @cached.prop
        def prop(self) -> int:
            return 1

        @cached.meth
        def meth_0(self) -> int:
            return 1

        @cached.meth
        def meth_1(self, x: float) -> float:
            return x * 2

        @cached.clear("meth_0", "meth_1")
        def clear(self) -> None:
            pass

    x = Example()

    assert x._cache == {}
    assert x.prop == 1
    assert x.meth_0() == 1
    assert x.meth_1(2.0) == 4.0

    for key in ["prop", "meth_0", "meth_1"]:
        assert key in x._cache

    x.clear()
    assert list(x._cache.keys()) == ["prop"]


def test_dataclass_class() -> None:
    @dataclasses.dataclass
    class Example:
        _cache: dict[str, Any] = dataclasses.field(default_factory=dict, init=False)  # pyright: ignore[reportUnknownVariableType]

        @cached.prop
        def prop(self) -> int:
            return 1

        @cached.meth
        def meth_0(self) -> int:
            return 1

        @cached.meth
        def meth_1(self, x: float) -> float:
            return x * 2

        @cached.clear("meth_0", "meth_1")
        def clear(self) -> None:
            pass

    x = Example()

    assert x._cache == {}
    assert x.prop == 1
    assert x.meth_0() == 1
    assert x.meth_1(2.0) == 4.0

    for key in ["prop", "meth_0", "meth_1"]:
        assert key in x._cache

    x.clear()
    assert list(x._cache.keys()) == ["prop"]


def test_dataclass_class_frozen() -> None:
    @dataclasses.dataclass(frozen=True)
    class Example:
        _cache: dict[str, Any] = dataclasses.field(default_factory=dict, init=False)  # pyright: ignore[reportUnknownVariableType]

        @cached.prop
        def prop(self) -> int:
            return 1

        @cached.meth
        def meth_0(self) -> int:
            return 1

        @cached.meth
        def meth_1(self, x: float) -> float:
            return x * 2

        @cached.clear("meth_0", "meth_1")
        def clear(self) -> None:
            pass

    x = Example()

    assert x._cache == {}
    assert x.prop == 1
    assert x.meth_0() == 1
    assert x.meth_1(2.0) == 4.0

    for key in ["prop", "meth_0", "meth_1"]:
        assert key in x._cache

    x.clear()
    assert list(x._cache.keys()) == ["prop"]
