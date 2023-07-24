# pyright: reportMissingTypeStubs=false
"""
Routies to interface docfiller with custom_inherit (mod:`~module_utilites.docinherit`)
======================================================================================
"""


from __future__ import annotations

try:
    from custom_inherit import doc_inherit  # pyright: ignore

    HAS_CUSTOM_INHERIT = True
except ImportError:
    HAS_CUSTOM_INHERIT = False  # pyright: ignore


if HAS_CUSTOM_INHERIT:
    from typing import Any, Callable, cast

    from ._typing import F, T_DocFiller
    from .options import DOC_SUB

    def doc_inherit_interface(
        parent: Callable[..., Any] | str,
        style: str = "numpy_with_merge",
    ) -> Callable[[F], F]:
        """Interface to custom_inherit.doc_inherit."""
        if DOC_SUB:
            return cast(
                Callable[[F], F],  # pyright: ignore
                doc_inherit(parent=parent, style=style),
            )
        else:

            def wrapper(func: F) -> F:
                return func

            return wrapper

    def factory_docfiller_from_parent(
        cls: Any, docfiller: T_DocFiller  # pyright: ignore
    ) -> Callable[..., Callable[[F], F]]:
        """Decorator with docfiller inheriting from cls"""

        def decorator(
            name_or_method: str | Callable[..., Any] | None = None, /, **params: str
        ) -> Callable[[F], F]:
            def decorated(method: F) -> F:
                if callable(name_or_method):
                    template = name_or_method
                else:
                    template = getattr(cls, name_or_method or method.__name__)
                return docfiller(template, _prepend=False, **params)(method)

            return decorated

        return decorator

    def factory_docinherit_from_parent(
        cls: Any, style: str = "numpy_with_merge"
    ) -> Callable[..., Callable[[F], F]]:
        """Create decorator inheriting from cls"""

        def decorator(
            name_or_method: str | Callable[..., Any] | None = None
        ) -> Callable[[F], F]:
            def decorated(method: F) -> F:
                if callable(name_or_method):
                    template = name_or_method
                else:
                    template = getattr(cls, name_or_method or method.__name__)
                return doc_inherit_interface(parent=template, style=style)(method)

            return decorated

        return decorator

    def factory_docfiller_inherit_from_parent(
        cls: Any,
        docfiller: T_DocFiller,  # pyright: ignore
        style: str = "numpy_with_merge",
    ) -> Callable[..., Callable[[F], F]]:
        """
        Do combination of doc_inherit and docfiller

        1. Fill parent and child with docfiller (from this module).
        2. Merge using doc_inherit
        """

        def decorator(
            name_or_method: str | Callable[..., Any] | None = None, /, **params: str
        ) -> Callable[[F], F]:
            def decorated(method: F) -> F:
                if callable(name_or_method):
                    template = name_or_method
                else:
                    template = getattr(cls, name_or_method or method.__name__)

                return docfiller.inherit(
                    template, _style=style, _prepend=False, **params
                )(method)

            return decorated

        return decorator
