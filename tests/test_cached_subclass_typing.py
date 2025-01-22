# pylint: disable=missing-class-docstring,no-self-use
from __future__ import annotations

from typing import Any

from module_utilities import cached


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

    @cached.meth
    def meth_cached(self, x: int) -> int:
        return x
