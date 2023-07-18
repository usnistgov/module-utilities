# pyre-ignore-all-errors[34]
"""
Cached class properties/methods (:mod:`~module_utilities.cached`)
=================================================================

Routines to define cached properties/methods in a class.
"""
from __future__ import annotations

from functools import wraps
from inspect import signature
from typing import (
    Any,
    Callable,
    Protocol,
    TypeVar,
    cast,
    overload,
)

from typing_extensions import Concatenate, Literal, ParamSpec, TypeAlias

__all__ = ["decorate", "prop", "meth", "clear"]

# from ._typing import F

P = ParamSpec("P")
R = TypeVar("R")


class HasCache(Protocol):
    _cache: dict[str, Any]


S = TypeVar("S", bound=HasCache)

C_prop: TypeAlias = Callable[[S], R]
C_meth: TypeAlias = Callable[Concatenate[S, P], R]  # pyre-ignore

D_prop: TypeAlias = Callable[[Callable[[S], R]], R]

# _T = TypeVar("_T", bound=HasCache, contravariant=True)
# _R = TypeVar("_R", covariant=True)

# class _PropProt(Protocol[_T, _R]):
#     __name__ : str
#     def __call__(self, __self: _T) ->  _R:...


@overload
def decorate(
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
    as_property: Literal[True] = ...,
) -> Callable[[C_prop[S, R]], R]:
    ...


@overload
def decorate(
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
    as_property: Literal[False],
) -> Callable[[C_meth[S, P, R]], C_meth[S, P, R]]:  # pyre-ignore
    ...


def decorate(
    *,
    key: str | None = None,
    check_use_cache: bool = False,
    as_property: bool = True,
) -> Callable[[C_prop[S, R]], R] | Callable[[C_meth[S, P, R]], C_meth[S, P, R]]:
    """
    General purpose cached decorator.

    Must always be called.
    """
    if as_property:
        return prop(key=key, check_use_cache=check_use_cache)
    else:
        return meth(key=key, check_use_cache=check_use_cache)


@overload
def prop(
    func: C_prop[S, R],
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
) -> R:
    ...


@overload
def prop(
    func: None = None, *, key: str | None = ..., check_use_cache: bool = ...
) -> Callable[[C_prop[S, R]], R]:
    ...


def prop(
    func: C_prop[S, R] | None = None,
    *,
    key: str | None = None,
    check_use_cache: bool = False,
) -> R | Callable[[C_prop[S, R]], R]:
    """
    Decorator to cache a property within a class.

    Parameters
    ----------
    _func: callable
        This parameter is used in the case that you decorate without ().
        That is, you can decorate with ``@prop`` or ``@prop()``.
    key : string, optional
        Optional key for storage in `_cache`.
        Default to attribute/method ``__name__``.
    check_use_cache : bool, default=False
        If `True`, then only apply caching if
        ``self._use_cache = True``.
        Note that the default value of `self._use_cache` is `False`.
        If `False`, then always apply caching.

    Notes
    -----
    To set `key` or `check_use_cache`, must pass with keyword.


    Examples
    --------
    >>> class A:
    ...    def __init__(self):
    ...        # this isn't strictly needed as it will be created on demand
    ...        # but should be included if using static typing (mypy, etc)
    ...        self._cache = {}
    ...
    ...    @cached.prop(key='keyname')
    ...    def size(self):
    ...        '''
    ...        This code gets ran only if the lookup of keyname fails
    ...        After this code has been ran once, the result is stored in
    ...        _cache with the key: 'keyname'
    ...        '''
    ...        print('set size')
    ...        return [10]
    ...
    ...    #no arguments implies give cache function name
    ...    @cached.prop
    ...    def myprop(self):
    ...        print('set myprop')
    ...        return [1.0]
    ...
    ...    @cached.prop(check_use_cache=True)
    ...    def checker(self):
    ...        print('set checker')
    ...        return [2.0]

    >>> x = A()
    >>> x.size
    set size
    [10]
    >>> x._cache['keyname'] is x.size
    True

    >>> x.size
    [10]

    >>> x.myprop
    set myprop
    [1.0]
    >>> x._cache['myprop'] is x.myprop
    True
    >>> x.myprop
    [1.0]

    If you pass ``check_use_cache=True`` and
    either `_use_cache=False` or the instance doens't have
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

    def cached_lookup(_func: C_prop[S, R]) -> R:
        if key is None:
            key_lookup = _func.__name__
        else:
            key_lookup = key

        @wraps(_func)
        def wrapper(self: S) -> R:
            if (not check_use_cache) or (getattr(self, "_use_cache", False)):
                try:
                    return cast(R, self._cache[key_lookup])
                except AttributeError:
                    self._cache = {}
                except KeyError:
                    pass

                self._cache[key_lookup] = ret = _func(self)
                return ret
            else:
                return _func(self)

        return property(wrapper)  # type: ignore

    if func:
        return cached_lookup(func)
    else:
        return cached_lookup


# @overload
# def meth(func: C_meth[S, P, R]) -> C_meth[S, P, R]: ...


@overload
def meth(
    func: C_meth[S, P, R],
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
) -> C_meth[S, P, R]:
    ...


@overload
def meth(
    func: None = None,
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
) -> Callable[[C_meth[S, P, R]], C_meth[S, P, R]]:
    ...


def meth(
    func: C_meth[S, P, R] | None = None,
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
    ...    @cached.meth(key='key')
    ...    def method(self, x, y=2):
    ...        # This code gets ran only if the lookup of keyname fails
    ...        # After this code has been ran once, the result is stored in
    ...        # _cache with the key: 'keyname'
    ...        # a long calculation....
    ...        print('calling method')
    ...        return [x, y]
    ...
    ...

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

    def cached_lookup(_func: C_meth[S, P, R]) -> C_meth[S, P, R]:
        if key is None:
            key_func = _func.__name__
        else:
            key_func = key

        # use signature
        bind = signature(_func).bind

        @wraps(_func)
        def wrapper(self: S, *args: P.args, **kwargs: P.kwargs) -> R:
            if (not check_use_cache) or (getattr(self, "_use_cache", False)):
                if not hasattr(self, "_cache"):
                    self._cache = {}

                if key_func not in self._cache:
                    self._cache[key_func] = {}

                params = bind(self, *args, **kwargs)
                params.apply_defaults()
                key_params = (
                    params.args[1:],
                    frozenset(params.kwargs.items()),
                )

                try:
                    return cast(R, self._cache[key_func][key_params])
                except TypeError:
                    # this means that key_lookup is bad hash
                    return _func(self, *args, **kwargs)
                # except AttributeError:
                #     self._cache = {}  # type: ignore
                except KeyError:
                    pass
                except Exception as e:
                    print(f"unknown exception {e} in meth call")
                    raise

                self._cache[key_func][key_params] = ret = _func(self, *args, **kwargs)
                return ret

            else:
                return _func(self, *args, **kwargs)

        return wrapper

    if func:
        return cached_lookup(func)
    else:
        return cached_lookup


@overload
def clear(key_or_func: C_meth[S, P, R], *keys: str) -> C_meth[S, P, R]:
    ...


@overload
def clear(key_or_func: str, *keys: str) -> Callable[[C_meth[S, P, R]], C_meth[S, P, R]]:
    ...


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
    ...    @cached.prop
    ...    def a(self):
    ...        print('calling a')
    ...        return 'a'
    ...
    ...    @cached.prop
    ...    def b(self):
    ...        print('calling b')
    ...        return 'b'
    ...
    ...    @cached.clear
    ...    def method_that_clears_all(self):
    ...        pass
    ...
    ...    @cached.clear('a')
    ...    def method_that_clears_a(self):
    ...        pass

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
        keys_inner = (key_or_func,) + keys

    def decorator(func: C_meth[S, P, R]) -> C_meth[S, P, R]:
        @wraps(func)
        def wrapper(self: S, *args: P.args, **kwargs: P.kwargs) -> R:
            # self._clear_caches(*keys_inner)
            # clear out keys_inner
            if hasattr(self, "_cache"):
                if len(keys_inner) == 0:
                    self._cache = {}
                else:
                    for name in keys_inner:
                        try:
                            del self._cache[name]
                        except KeyError:
                            pass

            return func(self, *args, **kwargs)

        return wrapper

    if function:
        return decorator(function)
    else:
        return decorator
