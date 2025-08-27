# pyright: reportMissingTypeStubs=false
"""
Routines to interface docfiller with custom_inherit (:mod:`~module_utilities.docinherit`)
=========================================================================================

Note that to use this module, you must install
`docstring-inheritanc <https://github.com/AntoineD/docstring-inheritance>`_

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from .docfiller import DocFiller
    from .typing import F

try:  # pylint: disable=too-many-try-statements
    import docstring_inheritance

    HAS_INHERIT = True
except ImportError:  # pragma: no cover
    HAS_INHERIT = False  # pyright: ignore[reportConstantRedefinition]


if HAS_INHERIT:
    from .options import DOC_SUB

    def doc_inherit(
        parent: Callable[..., Any] | str,
    ) -> Callable[[F], F]:
        """
        Decorator interface to docstring_inheritance.inherit_numpy_docstring

        Parameters
        ----------
        parent : callable or str
            Parent function to inherit from.

        Returns
        -------
        decorator : callable

        See Also
        --------
        module_utilities.docfiller.DocFiller.inherit

        Examples
        --------
        >>> from module_utilities.docfiller import DocFiller, indent_docstring
        >>> template = '''
        ... Parameters
        ... ----------
        ... x : {type_}
        ...     x parameter
        ... y : {type_}
        ...     y parameter
        ... '''

        >>> d_int = DocFiller.from_docstring(
        ...     template.format(type_="int"), combine_keys="parameters"
        ... )
        >>> d_float = DocFiller.from_docstring(
        ...     template.format(type_="float"), combine_keys="parameters"
        ... )
        >>> @d_int.decorate
        ... def func(x, y):
        ...     '''
        ...     A function
        ...
        ...     Parameters
        ...     ----------
        ...     {x}
        ...     {y}
        ...     '''
        ...     pass

        >>> @d_float.inherit(func)
        ... def func1(x, y, z):
        ...     '''
        ...     A new function
        ...
        ...     Parameters
        ...     ----------
        ...     z : str
        ...         z parameter
        ...     '''
        ...     pass

        >>> print(indent_docstring(func))
        +  A function
        <BLANKLINE>
        +  Parameters
        +  ----------
        +  x : int
        +      x parameter
        +  y : int
        +      y parameter

        >>> print(indent_docstring(func1))
        +  A new function
        <BLANKLINE>
        +  Parameters
        +  ----------
        +  x : float
        +      x parameter
        +  y : float
        +      y parameter
        +  z : str
        +      z parameter

        """
        docstring = parent.__doc__ or "" if callable(parent) else parent

        if DOC_SUB:

            def wrapper_inherit(func: F) -> F:
                docstring_inheritance.inherit_numpy_docstring(docstring, func)  # pyright: ignore[reportPossiblyUnboundVariable]
                return func

            return wrapper_inherit

        def wrapper_dummy(func: F) -> F:
            return func

        return wrapper_dummy

    def factory_docfiller_from_parent(
        cls: Any,
        docfiller: DocFiller,
    ) -> Callable[..., Callable[[F], F]]:
        """
        Decorator with docfiller inheriting from cls

        Note this returns a factory itself.

        See Also
        --------
        module_utilities.docfiller.DocFiller.factory_from_parent
        """

        def decorator(
            name_or_method: str | Callable[..., Any] | None = None,
            /,
            _prepend: bool = False,
            **params: str,
        ) -> Callable[[F], F]:
            def decorated(method: F) -> F:
                template = (
                    name_or_method
                    if callable(name_or_method)
                    else getattr(cls, name_or_method or method.__name__)
                )
                return docfiller(template, _prepend=_prepend, **params)(method)

            return decorated

        return decorator

    def factory_docinherit_from_parent(cls: Any) -> Callable[..., Callable[[F], F]]:
        """Create decorator inheriting from cls"""

        def decorator(
            name_or_method: str | Callable[..., Any] | None = None,
        ) -> Callable[[F], F]:
            def decorated(method: F) -> F:
                template = (
                    name_or_method
                    if callable(name_or_method)
                    else getattr(cls, name_or_method or method.__name__)
                )
                return doc_inherit(parent=template)(method)

            return decorated

        return decorator

    def factory_docfiller_inherit_from_parent(
        cls: Any,
        docfiller: DocFiller,
    ) -> Callable[..., Callable[[F], F]]:
        """
        Do combination of doc_inherit and docfiller

        1. Fill parent and child with docfiller (from this module).
        2. Merge using doc_inherit

        See Also
        --------
        module_utilities.docfiller.DocFiller.factory_inherit_from_parent
        """

        def decorator(
            name_or_method: str | Callable[..., Any] | None = None,
            /,
            _prepend: bool = False,
            **params: str,
        ) -> Callable[[F], F]:
            def decorated(method: F) -> F:
                template = (
                    name_or_method
                    if callable(name_or_method)
                    else getattr(cls, name_or_method or method.__name__)
                )
                return docfiller.inherit(template, _prepend=_prepend, **params)(method)

            return decorated

        return decorator
