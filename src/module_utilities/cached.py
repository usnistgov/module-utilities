"""Routines to define cached properties/methods in a class."""
from __future__ import annotations

from functools import wraps
from inspect import signature
from typing import Any, Callable, TypeVar, cast, overload

from typing_extensions import ParamSpec

__all__ = ["decorate", "prop", "meth", "clear"]

# from ._typing import F

P = ParamSpec("P")
R = TypeVar("R")


# @overload
# def decorate(
#     *, key=..., as_property: Literal[True] = ..., check_use_cache=...
# ) -> Callable[[Callable[[Any], R]], R]:
#     ...

# @overload
# def decorate(
#     *, key=..., as_property: Literal[False] = ..., check_use_cache=...
# ) -> Callable[[Callable[P, R]], Callable[P, R]]:
#     ...


def decorate(
    *, key: str | None = None, as_property: bool = True, check_use_cache: bool = False
):  # -> Callable[[Callable[[Any], R]], R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """
    General purpose cached decorator.

    Must always be called.
    """
    if as_property:
        return prop(key=key, check_use_cache=check_use_cache)
    else:
        return meth(key=key, check_use_cache=check_use_cache)


@overload
def prop(func: Callable[[Any], R]) -> R:
    ...


@overload
def prop(
    *, key: str | None = None, check_use_cache: bool = False
) -> Callable[[Callable[[Any], R]], R]:
    ...


def prop(
    func: Callable[[Any], R] | None = None,
    *,
    key: str | None = None,
    check_use_cache: bool = False,
) -> R | Callable[[Callable[[Any], R]], R]:
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
    ...        self._cache = dict()
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

    def cached_lookup(_func: Callable[[Any], R]) -> R:
        if key is None:
            key_inner = _func.__name__
        else:
            key_inner = key

        @wraps(_func)
        def wrapper(self) -> R:
            if (not check_use_cache) or (getattr(self, "_use_cache", False)):
                try:
                    return cast(R, self._cache[key_inner])
                except AttributeError:
                    self._cache = dict()
                except KeyError:
                    pass

                self._cache[key_inner] = ret = _func(self)
                return ret
            else:
                return _func(self)

        return property(wrapper)  # type: ignore

    if func:
        return cached_lookup(func)
    else:
        return cached_lookup


@overload
def meth(func: Callable[P, R]) -> Callable[P, R]:
    ...


@overload
def meth(
    *, key: str | None = None, check_use_cache: bool = False
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def meth(
    func: Callable[P, R] | None = None,
    *,
    key: str | None = None,
    check_use_cache: bool = False,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
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
    {('key', (1, 2), frozenset()): [1, 2]}

    See Also
    --------
    clear : corresponding decorator to remove cache
    prop : decorator for properties
    """

    def cached_lookup(_func: Callable[P, R]) -> Callable[P, R]:
        if key is None:
            key_inner = _func.__name__
        else:
            key_inner = key

        # use signature
        bind = signature(_func).bind

        @wraps(_func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            self = args[0]
            if (not check_use_cache) or (getattr(self, "_use_cache", False)):
                params = bind(*args, **kwargs)
                params.apply_defaults()
                key_func = (
                    key_inner,
                    params.args[1:],
                    frozenset(params.kwargs.items()),
                )
                try:
                    return cast(R, self._cache[key_func])  # type: ignore
                except TypeError:
                    # this means that key_func is bad hash
                    return _func(*args, **kwargs)
                except AttributeError:
                    self._cache = dict()  # type: ignore
                except KeyError:
                    pass

                self._cache[key_func] = ret = _func(*args, **kwargs)  # type: ignore
                return ret

            else:
                return _func(*args, **kwargs)

        return wrapper

    if func:
        return cached_lookup(func)
    else:
        return cached_lookup


@overload
def clear(key_or_func: Callable[P, R]) -> Callable[P, R]:
    ...


@overload
def clear(key_or_func: str, *keys: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def clear(
    key_or_func: str | Callable[P, R], *keys: str
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
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

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # self._clear_caches(*keys_inner)
            # clear out keys_inner
            self = args[0]
            if hasattr(self, "_cache"):
                if len(keys_inner) == 0:
                    self._cache = dict()
                else:
                    for name in keys_inner:
                        try:
                            del self._cache[name]
                        except KeyError:
                            pass

                    # functions
                    keys_tuples = [
                        k
                        for k in self._cache
                        if isinstance(k, tuple) and k[0] in keys_inner
                    ]
                    for k in keys_tuples:
                        del self._cache[k]
            return func(*args, **kwargs)

        return wrapper

    if function:
        return decorator(function)
    else:
        return decorator
