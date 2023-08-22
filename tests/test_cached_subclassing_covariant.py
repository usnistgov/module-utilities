from __future__ import annotations

from typing import Any

from module_utilities import cached
from functools import cached_property


class Base:
    _cache: dict[str, Any]

    @property
    def f_property(self) -> float:
        return 1.0

    @cached_property
    def f_functools(self) -> float:
        return 1.0

    @cached.prop
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
    def f_property(self) -> int:
        return 1

    @cached_property
    def f_functools(self) -> int:
        return 1

    @cached.prop
    def f_prop(self) -> float:
        return 1

    def f_method(self, x: int) -> float:
        return x

    @cached.meth
    def f_meth(self, x: int) -> int:
        return x


def test_stuff() -> None:
    b = Base()
    d = Derived0()

    c = Derived1()

    b.f_prop
