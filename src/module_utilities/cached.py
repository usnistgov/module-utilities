"""
Cached class properties/methods (:mod:`~module_utilities.cached`)
=================================================================

Routines to define cached properties/methods in a class.
"""
# pylint: disable=protected-access

from __future__ import annotations

import contextlib
from functools import update_wrapper, wraps
from inspect import signature
from operator import delitem
from typing import TYPE_CHECKING, Generic, cast, overload

from .typing import R, S

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import (
        Any,
        Literal,
    )

    from ._typing_compat import Self
    from .typing import C_meth, C_prop, P


__all__ = ["CachedProperty", "clear", "decorate", "meth", "prop"]


class CachedProperty(Generic[S, R]):
    """
    Simplified version of property with typing.

    Examples
    --------
    >>> class Example:
    ...     def __init__(self):
    ...         self._cache: dict[str, Any] = {}
    ...
    ...     def prop(self) -> int:
    ...         print("calling prop")
    ...         return 1
    ...
    ...     prop = CachedProperty(prop, key="hello")
    >>> x = Example()
    >>> print(x.prop)
    calling prop
    1
    >>> print(x.prop)
    1
    """

    def __init__(
        self, prop: C_prop[S, R], key: str | None = None, check_use_cache: bool = False
    ) -> None:
        self.__name__: str | None = None
        _ = update_wrapper(self, prop)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType, reportUnknownVariableType]

        self._prop = prop

        if key is None:
            key = prop.__name__

        if not isinstance(key, str):  # pyright: ignore[reportUnnecessaryIsInstance]  # pragma: no cover
            msg = f"key must be a string.  Passed {type(key)=}"  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
            raise TypeError(msg)
        self._key = key
        self._check_use_cache = check_use_cache

    def __set_name__(self, owner: type[Any], name: str) -> None:
        if self.__name__ is None:  # pragma: no cover
            self.__name__ = name
        elif name != self.__name__:  # pragma: no cover
            msg = (
                "Cannot assign the same TypedProperty to two different names "
                f"({self.__name__!r} and {name!r})."
            )
            raise TypeError(msg)

    @overload
    def __get__(self, instance: None, owner: type[Any] | None = None) -> Self: ...

    @overload
    def __get__(self, instance: S, owner: type[Any] | None = None) -> R: ...

    def __get__(self, instance: S | None, owner: type[Any] | None = None) -> Self | R:
        if instance is None:
            return self

        if (not self._check_use_cache) or (getattr(instance, "_use_cache", False)):
            try:
                return cast(
                    "R",
                    instance._cache[self._key],  # pyright: ignore [reportPrivateUsage]
                )
            except AttributeError:
                object.__setattr__(instance, "_cache", {})
            except KeyError:
                pass

            instance._cache[self._key] = ret = self._prop(instance)  # pyright: ignore[reportPrivateUsage]

            return ret

        return self._prop(instance)

    def __set__(self, instance: S | None, value: R) -> None:
        msg = f"can't set attribute {self._prop.__name__}"
        raise AttributeError(msg)


@overload
def decorate(
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
    as_property: Literal[False],
) -> Callable[[C_meth[S, P, R]], C_meth[S, P, R]]:  # pyre-ignore
    ...


@overload
def decorate(
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
    as_property: Literal[True] = ...,
) -> Callable[[C_prop[S, R]], CachedProperty[S, R]]: ...


@overload
def decorate(
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
    as_property: bool,
) -> (
    Callable[[C_meth[S, P, R]], C_meth[S, P, R]]
    | Callable[[C_prop[S, R]], CachedProperty[S, R]]
): ...


def decorate(
    *,
    key: str | None = None,
    check_use_cache: bool = False,
    as_property: bool = True,
) -> (
    Callable[[C_prop[S, R]], CachedProperty[S, R]]
    | Callable[[C_meth[S, P, R]], C_meth[S, P, R]]
):
    """
    General purpose cached decorator.

    Must always be called.
    """
    if as_property:
        return prop(key=key, check_use_cache=check_use_cache)
    return meth(key=key, check_use_cache=check_use_cache)


@overload
def prop(
    func: C_prop[S, R],
    /,
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
) -> CachedProperty[S, R]: ...


@overload
def prop(
    func: None = None, /, *, key: str | None = ..., check_use_cache: bool = ...
) -> Callable[[C_prop[S, R]], CachedProperty[S, R]]: ...


def prop(
    func: C_prop[S, R] | None = None,
    /,
    *,
    key: str | None = None,
    check_use_cache: bool = False,
) -> CachedProperty[S, R] | Callable[[C_prop[S, R]], CachedProperty[S, R]]:
    """
    Decorator to cache a property within a class.

    Parameters
    ----------
    func: callable
        This parameter is used in the case that you decorate without ().
        That is, you can decorate with ``@prop`` or ``@prop()``.
        Positional only.
    key : string, optional
        Optional key for storage in `_cache`.
        Default to attribute/method ``__name__``.
        Keyword only.
    check_use_cache : bool, default=False
        If `True`, then only apply caching if
        ``self._use_cache = True``.
        Note that the default value of `self._use_cache` is `False`.
        If `False`, then always apply caching.
        Keyword only.

    Notes
    -----
    To set `key` or `check_use_cache`, must pass with keyword.


    Examples
    --------
    >>> class A:
    ...     def __init__(self):
    ...         # this isn't strictly needed as it will be created on demand
    ...         # but should be included if using static typing (mypy, etc)
    ...         self._cache = {}
    ...
    ...     @prop(key="keyname")
    ...     def size(self):
    ...         '''
    ...         This code gets ran only if the lookup of keyname fails
    ...         After this code has been ran once, the result is stored in
    ...         _cache with the key: 'keyname'
    ...         '''
    ...         print("set size")
    ...         return [10]
    ...
    ...     # no arguments implies give cache function name
    ...     @prop
    ...     def myprop(self):
    ...         print("set myprop")
    ...         return [1.0]
    ...
    ...     @prop(check_use_cache=True)
    ...     def checker(self):
    ...         print("set checker")
    ...         return [2.0]

    >>> x = A()
    >>> x.size
    set size
    [10]
    >>> x._cache["keyname"] is x.size
    True

    >>> x.size
    [10]

    >>> x.myprop
    set myprop
    [1.0]
    >>> x._cache["myprop"] is x.myprop
    True
    >>> x.myprop
    [1.0]

    If you pass ``check_use_cache=True`` and
    either `_use_cache=False` or the instance doesn't have
    That property, then caching will NOT be done.

    >>> x.checker
    set checker
    [2.0]
    >>> x.checker
    set checker
    [2.0]


    See Also
    --------
    clear : corresponding decorator to clear cache
    meth : decorator for cache creation of function
    """

    def cached_lookup(_func: C_prop[S, R]) -> CachedProperty[S, R]:
        return CachedProperty[S, R](
            prop=_func, key=key, check_use_cache=check_use_cache
        )

    if func:
        return cached_lookup(func)
    return cached_lookup


@overload
def meth(
    func: C_meth[S, P, R],
    /,
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
) -> C_meth[S, P, R]: ...


@overload
def meth(
    func: None = None,
    /,
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
) -> Callable[[C_meth[S, P, R]], C_meth[S, P, R]]: ...


def meth(  # noqa: C901
    func: C_meth[S, P, R] | None = None,
    /,
    *,
    key: str | None = None,
    check_use_cache: bool = False,
) -> C_meth[S, P, R] | Callable[[C_meth[S, P, R]], C_meth[S, P, R]]:
    """
    Decorator to cache a function within a class

    Requires the Class to have a cache dict called ``_cache``.

    Examples
    --------
    >>> class A(object):
    ...     @meth(key="key")
    ...     def method(self, x, y=2):
    ...         # This code gets ran only if the lookup of keyname fails
    ...         # After this code has been ran once, the result is stored in
    ...         # _cache with the key: 'keyname'
    ...         # a long calculation....
    ...         print("calling method")
    ...         return [x, y]

    >>> x = A()
    >>> x.method(1, 2)
    calling method
    [1, 2]

    This will respect default params

    >>> x.method(1)
    [1, 2]

    And keyword arguments

    >>> x.method(y=2, x=1)
    [1, 2]
    >>> print(x._cache)
    {'key': {((1, 2), frozenset()): [1, 2]}}

    See Also
    --------
    clear : corresponding decorator to remove cache
    prop : decorator for properties
    """

    def cached_lookup(_func: C_meth[S, P, R]) -> C_meth[S, P, R]:  # noqa: C901
        key_func = _func.__name__ if key is None else key

        # use signature
        sig = signature(_func)

        if len(sig.parameters) == 1:
            # special case of single (self) parameter.
            @wraps(_func)
            def wrapper_no_args(self: S, /, *args: P.args, **kwargs: P.kwargs) -> R:
                if (not check_use_cache) or (getattr(self, "_use_cache", False)):
                    try:
                        return cast(
                            "R",
                            self._cache[key_func],  # pyright: ignore [reportPrivateUsage]
                        )
                    except AttributeError:
                        object.__setattr__(self, "_cache", {})  # noqa: PLC2801
                    except KeyError:
                        pass

                    self._cache[key_func] = ret = _func(self, *args, **kwargs)  # pyright: ignore [reportPrivateUsage]

                    return ret

                return _func(self, *args, **kwargs)

            return wrapper_no_args

        # Full method
        bind = sig.bind

        @wraps(_func)
        def wrapper_with_args(self: S, /, *args: P.args, **kwargs: P.kwargs) -> R:
            if (not check_use_cache) or (getattr(self, "_use_cache", False)):
                if not hasattr(self, "_cache"):
                    object.__setattr__(self, "_cache", {})  # noqa: PLC2801

                if key_func not in self._cache:  # pyright: ignore [reportPrivateUsage]
                    self._cache[key_func] = {}  # pyright: ignore [reportPrivateUsage]

                params = bind(self, *args, **kwargs)
                params.apply_defaults()
                key_params = (
                    params.args[1:],
                    frozenset(params.kwargs.items()),
                )

                try:
                    return cast("R", self._cache[key_func][key_params])  # pyright: ignore [reportPrivateUsage]
                except TypeError:
                    # this means that key_lookup is bad hash
                    return _func(self, *args, **kwargs)
                except KeyError:
                    pass
                except Exception as e:  # pragma: no cover
                    print(f"unknown exception {e} in meth call")  # noqa: T201
                    raise

                self._cache[key_func][key_params] = ret = _func(self, *args, **kwargs)  # pyright: ignore [reportPrivateUsage]
                return ret

            return _func(self, *args, **kwargs)

        return wrapper_with_args

    if func:
        return cached_lookup(func)

    return cached_lookup


@overload
def clear(key_or_func: C_meth[S, P, R], *keys: str) -> C_meth[S, P, R]: ...


@overload
def clear(
    key_or_func: str, *keys: str
) -> Callable[[C_meth[S, P, R]], C_meth[S, P, R]]: ...


def clear(
    key_or_func: str | C_meth[S, P, R], *keys: str
) -> C_meth[S, P, R] | Callable[[C_meth[S, P, R]], C_meth[S, P, R]]:
    """
    Decorator to clear self._cache of specified properties

    Parameters
    ----------
    *keys :
        Remove these keys from cache.  if len(keys)==0, remove all keys.


    Examples
    --------
    >>> class Example:
    ...     @prop
    ...     def a(self):
    ...         print("calling a")
    ...         return "a"
    ...
    ...     @prop
    ...     def b(self):
    ...         print("calling b")
    ...         return "b"
    ...
    ...     @clear
    ...     def method_that_clears_all(self):
    ...         pass
    ...
    ...     @clear("a")
    ...     def method_that_clears_a(self):
    ...         pass

    >>> x = Example()
    >>> x.a, x.b
    calling a
    calling b
    ('a', 'b')
    >>> x.a, x.b
    ('a', 'b')
    >>> x.method_that_clears_all()
    >>> x.a, x.b
    calling a
    calling b
    ('a', 'b')
    >>> x.a, x.b
    ('a', 'b')
    >>> x.method_that_clears_a()
    >>> x.a, x.b
    calling a
    ('a', 'b')


    See Also
    --------
    prop : corresponding decorator for cache creation of property
    meth : decorator for cache creation of function
    """
    if callable(key_or_func):
        function = key_or_func
        keys_inner = keys
    else:
        function = None
        keys_inner = (key_or_func, *keys)

    def decorator(func: C_meth[S, P, R]) -> C_meth[S, P, R]:
        @wraps(func)
        def wrapper(self: S, /, *args: P.args, **kwargs: P.kwargs) -> R:
            if hasattr(self, "_cache"):
                if not keys_inner:
                    self._cache.clear()  # pyright: ignore[reportPrivateUsage]
                else:
                    for name in keys_inner:
                        with contextlib.suppress(KeyError):
                            delitem(self._cache, name)  # pyright: ignore[reportPrivateUsage]

            return func(self, *args, **kwargs)

        return wrapper

    if function:
        return decorator(function)
    return decorator
