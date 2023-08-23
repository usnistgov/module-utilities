from __future__ import annotations

from module_utilities import cached

from typing import Any


class Base:
    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}

    @property
    def prop_property(self) -> int:
        return 1

    @property
    @cached.meth
    def prop_cached(self) -> int:
        return 1

    def meth(self, x: int) -> int:
        return x

    @cached.meth
    def meth_cached(self, x: int) -> int:
        return x


class Derived(Base):
    @property
    def prop_property(self) -> int:
        return 1

    @property
    @cached.meth
    def prop_cached(self) -> int:
        return 1

    # def meth(self, x: float) -> float:
    #     return x

    @cached.meth
    def meth_cached(self, x: int) -> int:
        return x
