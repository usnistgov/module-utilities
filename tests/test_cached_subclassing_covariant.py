# pylint: disable=missing-class-docstring,no-self-use
from __future__ import annotations

from functools import cached_property
from typing import Any

from module_utilities import cached


class Base:
    _cache: dict[str, Any]  # pyright: ignore[reportUninitializedInstanceVariable]

    @property
    def f_property(self) -> float:
        return 1.0

    @cached_property
    def f_functools(self) -> float:
        return 1.0

    @property
    @cached.meth
    def f_prop(self) -> float:
        return 1.0

    def f_method(self, x: int) -> float:
        return float(x)

    @cached.meth
    def f_meth(self, x: int) -> float:
        return float(x)


class Derived0(Base):
    pass


class Derived1(Base):
    @property
    def f_property(self) -> int:  # pyright: ignore[reportImplicitOverride]
        return 1

    @cached_property
    def f_functools(self) -> int:
        return 1

    @property
    @cached.meth
    def f_prop(self) -> int:
        return 1

    def f_method(self, x: int) -> float:  # pyright: ignore[reportImplicitOverride]
        return x

    @cached.meth
    def f_meth(self, x: int) -> int:
        return x


def test_stuff() -> None:
    b = Base()
    Derived0()

    Derived1()

    _ = b.f_prop
