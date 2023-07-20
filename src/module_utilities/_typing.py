"""Typing definitions"""

from __future__ import annotations

from typing import Any, Callable, Dict, Mapping, TypeVar, Union

# to maintain type information across generic functions and parametrization
# T = TypeVar("T")
# used in decorators to preserve the signature of the function it decorates
# see https://mypy.readthedocs.io/en/stable/generics.html#declaring-decorators
FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)


NestedMapVal = Union[str, "NestedMap"]
NestedMap = Mapping[str, NestedMapVal]


NestedDictVal = Union[str, "NestedDict"]
NestedDict = Dict[str, NestedDictVal]
