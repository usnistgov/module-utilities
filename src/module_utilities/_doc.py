"""
Taken directly from pandas.utils._decorators.doc
See https://github.com/pandas-dev/pandas/blob/main/pandas/util/_decorators.py
would just use the pandas version, but since it's a private
module, feel it's better to have static version here.
"""

from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable

    from .typing import F


def doc(
    *docstrings: None | str | Callable[..., Any], _prepend: bool = False, **params: str
) -> Callable[[F], F]:  # pyre-ignore
    """
    A decorator to take docstring templates, concatenate them and perform string
    substitution on them.
    This decorator will add a variable "_docstring_components" to the wrapped
    callable to keep track the original docstring template for potential usage.
    If it should be consider as a template, it will be saved as a string.
    Otherwise, it will be saved as callable, and later user __doc__ and dedent
    to get docstring.

    Parameters
    ----------
    *docstrings : None, str, or callable
        The string / docstring / docstring template to be appended in order
        after default docstring under callable.
    _prepend : bool, default=False
        If True, prepend decorated function docstring.  Otherwise, append to end.
    **params
        The string which would be used to format docstring template.

    """

    def decorator(decorated: F) -> F:
        # collecting docstring and docstring templates
        docstring_components: list[str | Callable[..., Any]] = []
        # if decorated.__doc__:
        #     docstring_components.append(dedent(decorated.__doc__))

        for docstring in docstrings:
            if docstring is None:
                continue
            if isinstance(docstring, str):
                docstring_components.append(docstring)
            elif hasattr(docstring, "_docstring_components"):
                docstring_components.extend(
                    docstring._docstring_components  # pyright: ignore[reportGeneralTypeIssues, reportFunctionMemberAccess, reportUnknownMemberType, reportUnknownArgumentType]
                )
            elif callable(docstring) and hasattr(docstring, "__doc__"):
                # docstring_components.append(docstring)
                docstring_components.append(dedent(docstring.__doc__ or ""))
            else:
                msg = f"Unknown docstring caught {type(docstring)=}"
                raise ValueError(msg)

        # make default to append
        if decorated.__doc__:
            if _prepend:
                docstring_components.insert(0, dedent(decorated.__doc__ or ""))
            else:
                docstring_components.append(dedent(decorated.__doc__ or ""))

        params_applied = [
            # component.format(**params)
            component.format_map(params)
            if isinstance(component, str) and len(params) > 0
            else component
            for component in docstring_components
        ]

        decorated.__doc__ = "".join(
            [
                component
                if isinstance(component, str)
                else dedent(component.__doc__ or "")
                for component in params_applied
            ]
        )

        # error: "F" has no attribute "_docstring_components"
        decorated._docstring_components = (  # type: ignore[attr-defined]
            docstring_components
        )
        return decorated

    return decorator
