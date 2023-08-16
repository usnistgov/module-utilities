"""
Typing definitions (:mod:`~module_utilities._typing`)
=====================================================
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Mapping, Protocol, TypeVar

from typing_extensions import Concatenate, ParamSpec, TypeAlias

# to maintain type information across generic functions and parametrization
# T = TypeVar("T")
# used in decorators to preserve the signature of the function it decorates
# see https://mypy.readthedocs.io/en/stable/generics.html#declaring-decorators

__all__ = [
    "NestedMapVal",
    "NestedMap",
    "NestedDictVal",
    "NestedDict",
    "F",
    "P",
    "R",
    "S",
    "C_meth",
    "C_prop",
    "HasCache",
    "T_DocFiller",
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


if TYPE_CHECKING:
    from .docfiller import DocFiller

T_DocFiller = TypeVar("T_DocFiller", bound="DocFiller")
"""Docfiller type"""
