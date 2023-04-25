"""Routines to define cached properties/methods in a class."""

from functools import wraps
from inspect import signature

__all__ = ["decorate", "prop", "meth", "clear"]

def decorate(key=None, as_property=True, check_use_cache=False):
    """General purpose cached decorator."""
    if as_property:
        return prop(key=key, check_use_cache=check_use_cache)
    else:
        return meth(key=key, check_use_cache=check_use_cache)


def prop(key=None, check_use_cache=False):
    """
    Decorator to cache a property within a class

    Notes
    -----
    Usage::

        class A(object):
           def__init__(self):
               # this isn't strictly needed as it will be created on demand
               self._cache = dict()

           @property
           @cached('keyname')
           def size(self):
               # This code gets ran only if the lookup of keyname fails
               # After this code has been ran once, the result is stored in
               # _cache with the key: 'keyname'
               size = 10.0

            #no arguments implies give cache function name
            @property
            @cached()
            def myprop(self):
                #results in _cache['myprop']

    See Also
    --------
    clear : corresponding decorator to clear cache
    meth : decorator for cache creation of function
    """

    if callable(key):
        func = key
        key = None
    else:
        func = None


    def cached_lookup(func):
        if key is None:
            key_inner = func.__name__
        else:
            key_inner = key

        @property
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if (not check_use_cache) or (getattr(self, "_use_cache", False)):
                try:
                    return self._cache[key_inner]
                except AttributeError:
                    self._cache = dict()
                except KeyError:
                    pass

                self._cache[key_inner] = ret = func(self, *args, **kwargs)
                return ret
            else:
                return func(self, *args, **kwargs)

        return wrapper

    if func:
        return cached_lookup(func)
    else:
        return cached_lookup


def meth(key=None, check_use_cache=False):
    """
    Decorator to cache a function within a class

    Requires the Class to have a cache dict called ``_cache``.

    Notes
    -----
    Usage::

        class A(object):
           def __init__(self):
              pass

           @meth('keyname')
           def amethod(self, *args):
               # This code gets ran only if the lookup of keyname fails
               # After this code has been ran once, the result is stored in
               # _cache with the key: 'keyname'
               # a long calculation...
               return long_calc(self,val)
               # if already executed result in _cache[('keyname',) + args]

            #no arguments implies give cache function name
            @property
            @cached()
            def myprop(self):
                #results in _cache['myprop']


    See Also
    --------
    clear : corresponding decorator to remove cache
    prop : decorator for properties
    """

    if callable(key):
        func = key
        key = None
    else:
        func = None

    def cached_lookup(func):
        if key is None:
            key_inner = func.__name__
        else:
            key_inner = key

        # use signature
        bind = signature(func).bind

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if (not check_use_cache) or (getattr(self, "_use_cache", False)):
                params = bind(self, *args, **kwargs)
                params.apply_defaults()
                key_func = (key_inner, params.args[1:], frozenset(params.kwargs.items()))
                try:
                    return self._cache[key_func]
                except TypeError:
                    # this means that key_func is bad hash
                    return func(self, *args, **kwargs)
                except AttributeError:
                    self._cache = dict()
                except KeyError:
                    pass

                self._cache[key_func] = ret = func(self, *args, **kwargs)
                return ret

            else:
                return func(self, *args, **kwargs)

        return wrapper

    if func:
        return cached_lookup(func)
    else:
        return cached_lookup


def clear(*keys):
    """
    Decorator to clear self._cache of specified properties

    Parameters
    ----------
    *keys : arguments
        remove these keys from cache.  if len(keys)==0, remove all keys.


    Examples
    --------
    Usage::

        class tmp(object)
            ...

            @property
            @cached()
            def a(self):
                ...

            @x.setter
            @clear('a','b')
            def x(self,val):
                #....
                #deletes self._cache['a'],self,_cache['b']
                #if args are empty, remove all


    See Also
    --------
    prop : corresponding decorator for cache creation of property
    meth : decorator for cache creation of function
    """

    if len(keys) == 1 and callable(keys[0]):
        function = keys[0]
        keys = ()
    else:
        function = None

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # self._clear_caches(*keys)
            # clear out keys
            if hasattr(self, "_cache"):
                if len(keys) == 0:
                    self._cache = dict()
                else:
                    for name in keys:
                        try:
                            del self._cache[name]
                        except KeyError:
                            pass

                    # functions
                    keys_tuples = [
                        k for k in self._cache if isinstance(k, tuple) and k[0] in keys
                    ]
                    for name in keys_tuples:
                        del self._cache[name]
            return func(self, *args, **kwargs)

        return wrapper

    if function:
        return decorator(function)
    else:
        return decorator
