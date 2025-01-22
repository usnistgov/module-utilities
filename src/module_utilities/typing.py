"""
Typing definitions (:mod:`~module_utilities.typing`)
=====================================================
"""
# pylint: disable=deprecated-typing-alias

from __future__ import annotations

from typing import Any, Callable, Mapping, Protocol, TypeVar

from ._typing_compat import Concatenate, ParamSpec, TypeAlias

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


class HasCache(Protocol):
    """Class protocol to mark that classes should have property _cache."""

    _cache: dict[str, Any]


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
