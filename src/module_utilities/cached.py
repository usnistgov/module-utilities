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
    TYPE_CHECKING,
    Callable,
    Generic,
    cast,
    overload,
)

from ._typing import C_meth, C_prop, P, R, S

if TYPE_CHECKING:
    from typing_extensions import (
        Literal,
        Self,
    )

__all__ = ["decorate", "prop", "meth", "clear", "TypedProperty"]  # , "HasCache", "S"]


class TypedProperty(Generic[S, R]):
    """
    Simplified version of property with typing.


    Examples
    --------
    >>> class Example:
    ...     def __init__(self):
    ...         self._cache: dict[str, Any] = {}
    ...
    ...     @TypedProperty
    ...     def prop(self) -> int:
    ...         return 1
    ...
    >>> x = Example()
    >>> print(x.prop)
    1

    """

    def __init__(self, getter: C_prop[S, R]) -> None:
        self.__name__: str | None = None
        self.getter = getter
        self.__doc__: str | None = getter.__doc__

    def __set_name__(self, owner: type[S], name: str) -> None:
        if self.__name__ is None:
            self.__name__ = name
        elif name != self.__name__:  # pragma: no cover
            raise TypeError(
                "Cannot assign the same TypedProperty to two different names "
                f"({self.__name__!r} and {name!r})."
            )

    @overload
    def __get__(self, instance: None, owner: type[S] | None = None) -> Self:
        ...

    @overload
    def __get__(self, instance: S, owner: type[S] | None = None) -> R:
        ...

    def __get__(self, instance: S | None, owner: type[S] | None = None) -> Self | R:
        if instance is None:
            return self
        return self.getter(instance)

    def __set__(self, instance: S | None, value: R) -> None:
        raise AttributeError(f"can't set attribute {self.__name__}")


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
) -> Callable[[C_prop[S, R]], TypedProperty[S, R]]:
    ...


def decorate(
    *,
    key: str | None = None,
    check_use_cache: bool = False,
    as_property: bool = True,
) -> (
    Callable[[C_prop[S, R]], TypedProperty[S, R]]
    | Callable[[C_meth[S, P, R]], C_meth[S, P, R]]
):
    """
    General purpose cached decorator.

    Must always be called.
    """
    if as_property:
        return prop(key=key, check_use_cache=check_use_cache)
    else:
        return meth(
            key=key, check_use_cache=check_use_cache
        )  # pyright: ignore[reportGeneralTypeIssues]


@overload
def prop(
    func: C_prop[S, R],
    /,
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
) -> TypedProperty[S, R]:
    ...


@overload
def prop(
    func: None = None, /, *, key: str | None = ..., check_use_cache: bool = ...
) -> Callable[[C_prop[S, R]], TypedProperty[S, R]]:
    ...


def prop(
    func: C_prop[S, R] | None = None,
    /,
    *,
    key: str | None = None,
    check_use_cache: bool = False,
) -> TypedProperty[S, R] | Callable[[C_prop[S, R]], TypedProperty[S, R]]:
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
    ...    def __init__(self):
    ...        # this isn't strictly needed as it will be created on demand
    ...        # but should be included if using static typing (mypy, etc)
    ...        self._cache = {}
    ...
    ...    @prop(key='keyname')
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
    ...    @prop
    ...    def myprop(self):
    ...        print('set myprop')
    ...        return [1.0]
    ...
    ...    @prop(check_use_cache=True)
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

    def cached_lookup(_func: C_prop[S, R]) -> TypedProperty[S, R]:
        if key is None:
            key_lookup = _func.__name__
        else:
            key_lookup = key

        @TypedProperty
        @wraps(_func)
        def wrapper(self: S) -> R:
            if (not check_use_cache) or (getattr(self, "_use_cache", False)):
                try:
                    return cast(
                        R,
                        self._cache[key_lookup],  # pyright: ignore [reportPrivateUsage]
                    )
                except AttributeError:
                    self._cache = {}  # pyright: ignore [reportPrivateUsage]
                except KeyError:
                    pass

                # fmt: off
                self._cache[key_lookup] = ret = _func(self)  # pyright: ignore [reportPrivateUsage]
                # fmt: on

                return ret
            else:
                return _func(self)

        return wrapper

    if func:
        return cached_lookup(func)
    else:
        return cached_lookup


# @overload
# def meth(func: C_meth[S, P, R]) -> C_meth[S, P, R]: ...


@overload
def meth(
    func: C_meth[S, P, R],
    /,
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
) -> C_meth[S, P, R]:
    ...


@overload
def meth(
    func: None = None,
    /,
    *,
    key: str | None = ...,
    check_use_cache: bool = ...,
) -> Callable[[C_meth[S, P, R]], C_meth[S, P, R]]:
    ...


def meth(
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
    ...    @meth(key='key')
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
        def wrapper(self: S, /, *args: P.args, **kwargs: P.kwargs) -> R:
            if (not check_use_cache) or (getattr(self, "_use_cache", False)):
                if not hasattr(self, "_cache"):
                    self._cache = {}  # pyright: ignore [reportPrivateUsage] # fmt: skip

                # fmt: off
                if (key_func not in self._cache):  # pyright: ignore [reportPrivateUsage]
                    self._cache[key_func] = {}  # pyright: ignore [reportPrivateUsage]
                # fmt: on

                params = bind(self, *args, **kwargs)
                params.apply_defaults()
                key_params = (
                    params.args[1:],
                    frozenset(params.kwargs.items()),
                )

                try:
                    # fmt: off
                    return cast(R, self._cache[key_func][key_params])  # pyright: ignore [reportPrivateUsage]
                    # fmt: on
                except TypeError:
                    # this means that key_lookup is bad hash
                    return _func(self, *args, **kwargs)
                # except AttributeError:
                #     self._cache = {}  # type: ignore
                except KeyError:
                    pass
                except Exception as e:  # pragma: no cover
                    print(f"unknown exception {e} in meth call")
                    raise

                # fmt: off
                self._cache[key_func][key_params] = ret = _func(self, *args, **kwargs) # pyright: ignore [reportPrivateUsage]
                # fmt: on
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
    ...    @prop
    ...    def a(self):
    ...        print('calling a')
    ...        return 'a'
    ...
    ...    @prop
    ...    def b(self):
    ...        print('calling b')
    ...        return 'b'
    ...
    ...    @clear
    ...    def method_that_clears_all(self):
    ...        pass
    ...
    ...    @clear('a')
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
        def wrapper(self: S, /, *args: P.args, **kwargs: P.kwargs) -> R:
            # self._clear_caches(*keys_inner)
            # clear out keys_inner
            if hasattr(self, "_cache"):
                if len(keys_inner) == 0:
                    self._cache = {}  # pyright: ignore [reportPrivateUsage]
                else:
                    for name in keys_inner:
                        try:
                            # fmt: off
                            del self._cache[name]  # pyright: ignore [reportPrivateUsage]
                            # fmt: on
                        except KeyError:
                            pass

            return func(self, *args, **kwargs)

        return wrapper

    if function:
        return decorator(function)
    else:
        return decorator


# def decorate2(
#     *,
#     key: str | None = None
#     check_use_cache: bool = False,
# ) ->  Callable[[C_meth[S, P, R]], C_meth[S, P, R]]:
#     """
#     General purpose cached decorator.

#     Must always be called.
#     """
#     # return cast(Callable[[C_meth[S, P, R]], C_meth[S, P, R]], meth(key=key, check_use_cache=check_use_cache))
#     return meth(key=key, check_use_cache=check_use_cache)


# reveal_type(meth(key='hello', check_use_cache=True))
# reveal_type(decorate(key='hello', check_use_cache=True, as_property=False))
# reveal_type(decorate2(key='hello'))


# class tmp:
#     _cache: dict[str, Any] = {}

#     @meth()
#     def hello(self, x: int, y: float) -> Callable[[float], float]:
#         def func(z: float) -> float:
#             return x + y + z

#         return func

#     @prop()
#     def there(self) -> Callable[[int], int]:
#         def func(x: int) -> int:
#             return x

#         return func

#     @property
#     @meth
#     def there2(self) -> Callable[[int], int]:
#         def func(x: int) -> int:
#             return x

#         return func


# x = tmp()

# if TYPE_CHECKING:
#     # reveal_type(x.hello)
#     # reveal_type(x.hello(1, 2))
#     # reveal_type(x.there)
#     # reveal_type(x.there(1))
#     # reveal_type(x.there2)
#     # reveal_type(x.there2(1))

#     # f: Callable[[S,int], float]

#     # reveal_type(meth(f))
#     # reveal_type(meth(key='hello')(f))
#     # reveal_type(meth(f, key='hello'))

#     # from typing_extensions import get_overloads

#     # get_overloads(prop)

#     def fprop(self: S) -> str:
#         return "hello"

#     def fmeth(self: S, x: str) -> str:
#         return x + "there"

#     # reveal_type(prop(fprop))
#     # reveal_type(prop(fprop, key='hello'))
#     # reveal_type(prop(fprop, check_use_cache=True))
#     # reveal_type(prop(fprop, key='hello', check_use_cache=False))

#     # reveal_type(prop(key='hello'))
#     # reveal_type(prop(check_use_cache=True))
#     # reveal_type(prop(check_use_cache=False, key='some'))

#     # reveal_type(prop(key='hello')(fprop))
#     # reveal_type(prop(check_use_cache=True)(fprop))
#     # reveal_type(prop(check_use_cache=False, key='some')(fprop))

#     def decorate_meth(
#         *,
#         key: str | None = None,
#         check_use_cache: bool = False,
#         as_property: bool = True,
#     ) -> Callable[[C_meth[S, P, R]], C_meth[S, P, R]]:
#         """
#         General purpose cached decorator.

#         Must always be called.
#         """
#         return meth(key=key, check_use_cache=check_use_cache)

#     reveal_type(decorate())
#     reveal_type(decorate(key="hello"))
#     reveal_type(decorate(check_use_cache=True))
#     reveal_type(decorate(as_property=True))

#     reveal_type(decorate(as_property=False))
#     reveal_type(meth())
#     reveal_type(decorate(key="there", as_property=False))
#     reveal_type(decorate(key="something", check_use_cache=True, as_property=False))

#     reveal_type(decorate_meth(as_property=False))
#     reveal_type(meth())
#     reveal_type(decorate_meth(key="there", as_property=False))
#     reveal_type(decorate_meth(key="something", check_use_cache=True, as_property=False))

#     # reveal_type(decorate(key='hello')(fprop))
#     # reveal_type(prop(fprop, check_use_cache=True))
#     # reveal_type(prop(fprop, key='hello', check_use_cache=False))

#     # reveal_type(prop(key='hello'))
#     # reveal_type(prop(check_use_cache=True))
#     # reveal_type(prop(check_use_cache=False, key='some'))

#     # reveal_type(prop(key='hello')(fprop))
#     # reveal_type(prop(check_use_cache=True)(fprop))
#     # reveal_type(prop(check_use_cache=False, key='some')(fprop))

#     # reveal_type(meth(fmeth))
#     # reveal_type(meth(fmeth, key='hello'))
#     # reveal_type(meth(fmeth, check_use_cache=True))
#     # reveal_type(meth(fmeth, key='hello', check_use_cache=False))

#     # reveal_type(meth(key='hello'))
#     # reveal_type(meth(check_use_cache=True))
#     # reveal_type(meth(check_use_cache=False, key='some'))

#     # reveal_type(meth(key='hello')(fmeth))
#     # reveal_type(meth(check_use_cache=True)(fmeth))
#     # reveal_type(meth(check_use_cache=False, key='some')(fmeth))
