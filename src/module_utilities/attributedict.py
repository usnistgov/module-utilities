"""
Attribute dictionary (:mod:`~module_utilities.attibutedict`)
============================================================
"""
from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Any

# from typing import TypeVar, Type

# AttibuteDictT = TypeVar('AttributeDictT', bound="AttributeDict")


def _get_nested_values(d, join_string="\n"):
    out = []
    for k in d:
        v = d[k]
        if isinstance(v, str):
            out.append(v)
        else:
            out.extend(_get_nested_values(v, join_string=None))

    if join_string is not None:
        out = join_string.join(out)

    return out


class AttributeDict(MutableMapping):
    """
    Dictionary with recursive attribute like access.

    To be used in str.format calls, so can expand on fields like
    `{name.property}` in a nested manner.

    Parameters
    ----------
    entries : dict
    recursive : bool, default=True
        If True, recursively return ``AttributeDict`` for nested dicts.
    allow_missing : bool, defualt=True
        If True, allow missing keys.

    Example
    -------
    >>> d = AttributeDict({"a": 1, "b": {"c": 2}})
    >>> d.a
    1
    >>> d.b
    AttributeDict({'c': 2})
    >>> d.b.c
    2
    """

    __slots__ = ("_entries", "_recursive", "_allow_missing")

    def __init__(
        self,
        entries: dict[str, Any] | None = None,
        recursive: bool = True,
        allow_missing: bool = True,
    ):
        if entries is None:
            entries = {}
        self._entries = entries
        self._recursive = recursive
        self._allow_missing = allow_missing

    def __getitem__(self, key: str | slice) -> Any:
        if isinstance(key, slice):
            return _get_nested_values(self._getslice(key), join_string="\n")

        if key == ":":
            return _get_nested_values(self._entries, join_string="\n")

        elif "," in key:
            return "\n".join(self[x] for x in (x.strip() for x in key.split(",")))

        if self._allow_missing and key not in self._entries:
            return f"{{{key}}}"
        else:
            return self._entries[key]

    def _getslice(self, s) -> AttributeDict:
        start = s.start
        stop = s.stop

        keys = list(self._entries.keys())

        if isinstance(s.start, int) or s.start is None and isinstance(s.stop, int):
            slc = s

        else:
            if s.start is None:
                start = 0
            else:
                start = keys.index(s.start)

            if s.stop is None:
                stop = len(self) + 1
            else:
                stop = keys.index(s.stop) + 1

            slc = slice(start, stop, s.step)

        subset = {k: self._entries[k] for k in keys[slc]}
        return type(self)(subset)

    def __setitem__(self, key: str, value) -> None:
        self._entries[key] = value

    def __iter__(self):
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __delitem__(self, key):
        del self._entries[key]

    def _items(self):
        yield from self._entries.items()

    def __dir__(self):
        return list(self.keys()) + list(super().__dir__())

    def _update(self, *args, **kwargs):
        self._entries.update(*args, **kwargs)

    def __getattr__(self, attr):
        if attr in self._entries:
            out = self._entries[attr]
            if self._recursive and isinstance(out, dict):
                out = type(self)(out)
            return out
        else:
            try:
                return self.__getattribute__(attr)
            except AttributeError as err:
                # If Python is run with -OO, it will strip docstrings and our lookup
                # from self._entries will fail. We check for __debug__, which is actually
                # set to False by -O (it is True for normal execution).
                # But we only want to see an error when building the docs;
                # not something users should see, so this slight inconsistency is fine.
                if __debug__:
                    raise err
                else:
                    pass

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self._entries)})"

    @classmethod
    def _from_dict(
        cls, params: Mapping, max_level: int = 1, level: int = 0, recursive: bool = True
    ) -> AttributeDict:
        # to hide level parameter
        out = cls(recursive=recursive)
        for k in params:
            v = params[k]
            if isinstance(v, dict) and level < max_level:
                v = cls._from_dict(
                    v, max_level=max_level, level=level + 1, recursive=recursive
                )
            out[k] = v
        return out

    @classmethod
    def from_dict(
        cls, params: Mapping, max_level: int = 1, recursive: bool = True
    ) -> AttributeDict:
        """
        Create AttributeDict recursively for nested dictionaries.

        To be used in cases where need to apply AttibuteDict to parameters
        passed with ``func(**params)``.


        Parameters
        ----------
        params : mapping
            Mapping to apply cls to.
        max_level : int, default=1
            How deep to apply cls to.
        recursive : bool, default=True
            ``recursive`` parameter of resulting object.

        Returns
        -------
        AttributeDict

        Examples
        --------
        >>> d = {"a": "p0", "b": {"c": {"d": "d0"}}}
        >>> AttributeDict.from_dict(d, max_level=1)
        AttributeDict({'a': 'p0', 'b': AttributeDict({'c': {'d': 'd0'}})})

        >>> AttributeDict.from_dict(d, max_level=2)
        AttributeDict({'a': 'p0', 'b': AttributeDict({'c': AttributeDict({'d': 'd0'})})})

        """
        return cls._from_dict(
            params=params, max_level=max_level, level=0, recursive=recursive
        )
