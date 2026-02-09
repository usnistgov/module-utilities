"""
Typing definitions (:mod:`~module_utilities.typing`)
=====================================================
"""
# pylint: disable=deprecated-typing-alias

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping
from typing import Any, Concatenate, ParamSpec, Protocol, TypeAlias, TypeVar

__all__ = [
    "C_meth",
    "C_prop",
    "F",
    "HasCache",
    "NestedDict",
    "NestedDictVal",
    "NestedMap",
    "NestedMapVal",
    "P",
    "R",
    "S",
]

FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)
"""Function type"""


# cached stuff

P = ParamSpec("P")
"""Parameter specification"""

R = TypeVar("R")
"""Return Type"""


class HasCacheAttribute(Protocol):
    """Class protocol to mark class should have _cache attribute"""

    _cache: MutableMapping[str, Any]


class HasCacheProperty(Protocol):
    """
    Class protocol to mark that classes should have property _cache.

    NOTE: strictly speaking, this should be read/writeable
    but for attrs, frozen to work, need to pretend its read only.
    Use some tricks to make it work from there...
    """

    @property
    def _cache(self) -> MutableMapping[str, Any]: ...  # pragma: no cover


HasCache: TypeAlias = HasCacheAttribute | HasCacheProperty
"""Protocol to mark that class should have ``_cache`` attribute"""


S = TypeVar("S", bound="HasCache")
"""Self Type bound to HasCache"""

C_prop: TypeAlias = Callable[[S], R]
C_meth: TypeAlias = Callable[Concatenate[S, P], R]  # pyre-ignore

# docfiller stuff

NestedMapVal: TypeAlias = "str | NestedMap"
"""Nested map value type"""
NestedMap: TypeAlias = Mapping[str, NestedMapVal]
"""Nested map type"""


NestedDictVal: TypeAlias = "str | NestedDict"
"""Nested dict value type"""
NestedDict: TypeAlias = "dict[str, NestedDictVal]"
"""Nested dict type"""
