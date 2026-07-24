# ruff:file-ignore[commented-out-code]
# pylint: disable=no-self-use,missing-class-docstring
from __future__ import annotations

import sys
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from module_utilities import docinherit
from module_utilities.docfiller import DocFiller

if sys.version_info >= (3, 11):
    from typing import assert_type
else:
    from typing_extensions import assert_type  # pyright: ignore[reportUnreachable]

if TYPE_CHECKING:
    from typing import Any, TypeVar

    T = TypeVar("T")


pytestmark = [
    pytest.mark.inherit,
    pytest.mark.skipif(
        not docinherit.HAS_INHERIT, reason="docstring_inheritance not installed"
    ),
]


def check(
    actual: T,
    klass: type[Any],
) -> T:
    assert isinstance(actual, klass)
    return actual


_docs = """
A program


Parameters
----------
a : int
    an int
b : float
    a float
out : float, optional
    A float out
"""


docfiller = DocFiller.from_docstring(_docs, combine_keys="parameters")


class Template:
    """A thing"""

    @docfiller.decorate
    def func0(self, a: int) -> int | None:
        """
        Parameters
        ----------
        {a}

        Returns
        -------
        {out}
        """
        return a


def test_stuff() -> None:

    docfiller_inherit = docfiller.factory_inherit_from_parent(Template)

    @docfiller(Template)
    class Other:
        @docfiller_inherit()  # this fails for ty
        def func0(self, a: int) -> int:
            return a

    class Other2:
        @docfiller.inherit(Template.func0)
        def func0(self, a: int) -> int:
            return a

    expected = "A thing"
    assert Template.__doc__ == expected
    assert Other.__doc__ == expected

    expected = dedent("""
    Parameters
    ----------
    a : int
        an int

    Returns
    -------
    out : float, optional
        A float out
    """).strip()

    for cls in (Template, Other, Other2):
        assert isinstance(cls.func0.__doc__, str)
        assert cls.func0.__doc__.strip() == expected

    check(assert_type(Template().func0(1), int | None), int)
    # check(assert_type(Other().func0(1), int), int)  # this fails for ty
    check(assert_type(Other2().func0(1), int), int)

    # if TYPE_CHECKING:
    #     from typing import reveal_type

    #     reveal_type(Template.func0)
    #     reveal_type(Other.func0)
    #     reveal_type(Other2.func0)
