"""Typing definitions"""

from typing import Any, Callable, TypeVar

# to maintain type information across generic functions and parametrization
# T = TypeVar("T")
# used in decorators to preserve the signature of the function it decorates
# see https://mypy.readthedocs.io/en/stable/generics.html#declaring-decorators
FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)
