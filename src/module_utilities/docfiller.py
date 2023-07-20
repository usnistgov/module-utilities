"""
Fill and share documentation (:mod:`module_utilities.docfiller`)
================================================================
"""
from __future__ import annotations

import inspect
import os
from collections.abc import Mapping
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Callable, Iterable, cast

from . import cached
from ._doc import doc as _pd_doc
from .attributedict import AttributeDict
from .vendored.docscrape import NumpyDocString, Parameter

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ._typing import F, NestedMap, NestedMapVal

try:
    # Default is DOC_SUB is True
    DOC_SUB = os.getenv("DOCFILLER_SUB", "True").lower() not in (
        "0",
        "f",
        "false",
    )
except KeyError:
    DOC_SUB = True


# Factory method to create doc_decorate
def doc_decorate(
    *docstrings: str | Callable[..., Any],
    _prepend: bool = False,
    **params: str,
) -> Callable[[F], F]:
    """
    A decorator take docstring templates, concatenate them and perform string
    substitution on it.

    This decorator will add a variable "_docstring_components" to the wrapped
    callable to keep track the original docstring template for potential usage.
    If it should be consider as a template, it will be saved as a string.
    Otherwise, it will be saved as callable, and later user __doc__ and dedent
    to get docstring

    Parameters
    ----------
    *docstrings : str or callable
        The string / docstring / docstring template to be appended in order
        after default docstring under callable.
    _prepend : bool, default=False
        If True, prepend decorated function docstring.  Otherwise, append to end.
    **params
        The string which would be used to format docstring template.

    Notes
    -----
    Doc filling can be turned off by setting the environment variable
    ``DOCFILLER_SUB`` to one of ``0, f, false``.
    """

    if DOC_SUB:
        return _pd_doc(*docstrings, _prepend=_prepend, **params)
    else:

        def decorated(func: F) -> F:
            return func

        return decorated


def _build_param_docstring(name: str, ptype: str, desc: str | Sequence[str]) -> str:
    """
    Create multiline documentation of single name, type, desc.

    Parameters
    ----------
    ==========
    name : str
        Parameter Name
    ptype : str
        Parameter type
    desc : list of str
        Parameter description

    Returns
    -------
    output : string
        Multiline string for output.

    """

    no_name = name is None or name == ""
    no_type = ptype is None or ptype == ""

    if no_name and no_type:
        raise ValueError("must specify name or ptype")
    elif no_type:
        s = f"{name}"
    elif no_name:
        s = f"{ptype}"
    else:
        s = f"{name} : {ptype}"

    if isinstance(desc, str):
        if desc == "":
            desc = []
        else:
            desc = [desc]

    elif len(desc) == 1 and desc[0] == "":
        desc = []

    if len(desc) > 0:
        desc = "\n    ".join(desc)
        s += f"\n    {desc}"
    return s


def _params_to_string(
    params: str | list[str] | Parameter | list[Parameter] | tuple[Parameter, ...],
    key_char: str = "|",
) -> str | dict[str, str]:
    """
    Parse list of Parameters objects to string

    Examples
    --------
    >>> from module_utilities.docfiller import Parameter
    >>> p = Parameter(name="a", type="int", desc=["A parameter"])
    >>> out = _params_to_string(p)
    >>> print(out["a"])
    a : int
        A parameter
    """

    if len(params) == 0:
        return ""

    if isinstance(params, Parameter):
        params = [params]

    if not isinstance(params, (list, tuple)):
        params = [params]

    if isinstance(params[0], str):
        return "\n".join(cast(list[str], params))

    out = {}
    for p in cast(list[Parameter], params):
        name = p.name
        if key_char in name:
            key, name = (x.strip() for x in name.split(key_char))
        else:
            key = name

        out[key] = _build_param_docstring(name=name, ptype=p.type, desc=p.desc)

    return out


def _parse_docstring(
    func_or_doc: Callable[..., Any] | str, key_char: str = "|", expand: bool = True
) -> dict[str, str | dict[str, str]]:
    """
    Parse numpy style docstring from function or string to dictionary.

    Parameters
    ----------
    func_or_doc : callable or str
        If function, extract docstring from function.
    key_char : str, default='|'
        Character to split key_name/name
    expand : bool, default=False

    Returns
    -------
    parameters : dict
        Dictionary with keys from docstring sections.

    Notes
    -----
    the keys of ``parameters`` have the are the those of the numpy docstring,
    but lowercase, and spaces replaced with underscores.  The sections parsed are:
    Summary, Extended Summary, Parameters, Returns, Yields, Notes,
    Warnings, Other Parameters, Attributes, Methods, References, and Examples.

    Examples
    --------
    >>> doc_string = '''
    ... Parameters
    ... ----------
    ... x : int
    ...     x parameter
    ... y_alt | y : float
    ...     y parameter
    ...
    ... Returns
    ... -------
    ... output : float
    ...     an output
    ... '''

    >>> p = _parse_docstring(doc_string)
    >>> print(p["parameters"]["x"])
    x : int
        x parameter
    >>> print(p["parameters"]["y_alt"])
    y : float
        y parameter
    >>> print(p["returns"]["output"])
    output : float
        an output


    """

    if callable(func_or_doc):
        doc = inspect.getdoc(func_or_doc)
    else:
        doc = func_or_doc

    parsed = cast(dict[str, str | list[str] | list[Parameter]], NumpyDocString(doc)._parsed_data)  # type: ignore[no-untyped-call]

    if expand:
        parsed_out = {
            k.replace(" ", "_").lower(): _params_to_string(parsed[k], key_char=key_char)
            for k in [
                "Summary",
                "Extended Summary",
                "Parameters",
                "Returns",
                "Yields",
                "Notes",
                "Warnings",
                "Other Parameters",
                "Attributes",
                "Methods",
                "References",
                "Examples",
            ]
        }
    else:
        parsed_out = cast(dict[str, str | dict[str, str]], parsed)
    return parsed_out


def dedent_recursive(data: NestedMap) -> NestedMap:
    """
    Dedent nested mapping of strings.

    Parameters
    ----------
    data : dict

    Returns
    -------
    output : object
        Same type of ``data``, with dedented values

    Examples
    --------
    >>> data = {
    ...     'a': {'value' : '''
    ...      a : int
    ...          A thing
    ...      '''}}
    >>> print(data['a']['value'])
    <BLANKLINE>
         a : int
             A thing
    <BLANKLINE>
    >>> data = dedent_recursive(data)
    >>> print(data['a']['value'])
    a : int
        A thing
    """
    out = {}
    for k in data:
        v = data[k]
        if isinstance(v, str):
            v = dedent(v).strip()
        else:
            v = dedent_recursive(v)
        out[k] = v
    return out


def _recursive_keys(data: NestedMap) -> list[str]:
    keys = []
    for k, v in data.items():
        if isinstance(v, dict):
            key_list = [f"{k}.{x}" for x in _recursive_keys(v)]
        elif isinstance(v, str):
            key_list = [k]
        else:
            raise ValueError(f"unknown type {type(v)}")

        keys.extend(key_list)

    return keys


class DocFiller:
    """
    Class to handle doc filling.

    Parameters
    ----------
    func_or_doc : callable or str
        Docstring to parse.  If callable, extract from function signature.
    key_char : str, default='|'
        Optional string to split name into key/name pair.
    """

    def __init__(self, params: NestedMap | None = None) -> None:
        self.data: dict[str, NestedMapVal]

        if params is None:
            self.data = {}
        elif isinstance(params, dict):
            self.data = params
        else:
            self.data = dict(params)
        self._cache: dict[str, Any] = {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.data)})"

    def new_like(self, data: NestedMap | None = None) -> DocFiller:
        """Create new object with optional data."""
        if data is None:
            data = self.data.copy()
        return type(self)(data)

    def __getitem__(self, key: str) -> DocFiller | str:
        val = self.data[key]
        if isinstance(val, Mapping):
            return self.new_like(val)
        else:
            return val

    def dedent(self) -> DocFiller:
        """Recursively dedent params"""
        return self.new_like(dedent_recursive(self.data))

    @cached.meth
    def keys(self) -> list[str]:
        """List of keys"""
        return _recursive_keys(self.data)

    def assign_combined_key(self, new_key: str, keys: Sequence[str]) -> DocFiller:
        """Combine multiple keys into single key"""
        new = self.new_like()

        new_data: list[str] = []
        for k in keys:
            d = self.data[k]
            if isinstance(d, str):
                new_data.append(d)
            else:
                raise ValueError(f"trying to combine key {k} with non-string value {d}")

        new.data[new_key] = "\n".join(new_data)
        return new

    def _gen_get_val(self, key: str) -> Any:
        from operator import attrgetter

        f = attrgetter(key)
        return f(self.params)

    def assign_keys(self, **kwargs: str | Sequence[str]) -> DocFiller:
        """
        Create new key from other keys.

        Parameters
        ----------
        **kwargs
            new_key=old_key or new_key=[old_key0, old_key1, ...]
            Note that dot notation is accepted.


        Examples
        --------
        >>> d = DocFiller({'a0': 'a0', 'a1': 'a1', 'b': 'b'})
        >>> dn = d.assign_keys(a='a0', c=['a0','b']).data
        >>> print(dn['a'])
        a0

        >>> print(dn['c'])
        a0
        b


        """
        new = self.new_like()
        for new_key, old_keys in kwargs.items():
            if isinstance(old_keys, str):
                keys = [old_keys]
            else:
                keys = list(old_keys)

            new.data[new_key] = "\n".join([self._gen_get_val(k) for k in keys])

        return new

    def assign_param(
        self,
        name: str,
        ptype: str = "",
        desc: str | list[str] | None = None,
        key: str | None = None,
    ) -> DocFiller:
        """
        Add in a new parameter

        Parameters
        ----------
        name : str
            Parameters name
        key : str, optional
            Optional key for placement in `self`.  This is like using `key | name`.
        ptype : str, default=''
            Optional type.
        desc : str or list of str, default=''
            Parameter description.

        Returns
        -------
        output : DocFiller
            New DocFiller instance.

        Examples
        --------
        >>> d = DocFiller()
        >>> dn = d.assign_param(
        ...     name='x',
        ...     ptype='float',
        ...     desc='''
        ...     A parameter
        ...     with multiple levels
        ...     ''',
        ... )
        >>> print(dn['x'])
        x : float
            A parameter
            with multiple levels
        """

        new = self.new_like()

        if desc is None:
            desc = []
        elif isinstance(desc, str):
            # cleanup desc
            desc = dedent(desc).strip().split("\n")

        key = name if key is None else key

        new.data[key] = _build_param_docstring(name=name, ptype=ptype, desc=desc)

        return new

    @classmethod
    def concat(
        cls,
        *args: NestedMap | DocFiller,
        **kwargs: NestedMap | DocFiller,
    ) -> DocFiller:
        """
        Create new object from multiple DocFiller or dict objects.

        Parameters
        ----------
        *args
            dict or Docfiller
        **kwargs
            dict or Docfiller objects
            The passed name will be used as the top level.

        Returns
        -------
        DocFiller
            combined DocFiller object.

        Notes
        -----
        Use unnamed `args` to pass in underlying data.
        Use names ``kwargs`` to add namespace.
        """

        # create

        data: dict[str, NestedMapVal] = {}

        def _update_data(x: DocFiller | NestedMap | dict[str, NestedMap]) -> None:
            if isinstance(x, DocFiller):
                # x = x.params
                x = x.data
            data.update(**x)

        for a in args:
            _update_data(a)

        kws: dict[str, NestedMap] = {}
        for k, v in kwargs.items():
            if isinstance(v, DocFiller):
                kws[k] = v.data
            else:
                kws[k] = v

        _update_data(kws)
        return cls(data)

    def append(
        self,
        *args: Mapping[str, Any] | DocFiller,
        **kwargs: Mapping[str, Any] | DocFiller,
    ) -> DocFiller:
        """Calls ``concat`` method with ``self`` as first argument."""
        return type(self).concat(self, *args, **kwargs)

    def insert_level(self, name: str) -> DocFiller:
        """Insert a level/namespace."""
        return type(self)({name: self.data})

    def levels_to_top(self, *names: str) -> DocFiller:
        """Make a level top level accessible"""

        new = self.new_like()
        for name in names:
            d = self.data[name]
            if isinstance(d, str):
                raise ValueError(f"level {name} is not a dict")
            else:
                for k, v in d.items():
                    new.data[k] = v
        return new

    def rename_levels(self, **kws: str) -> DocFiller:
        """Rename a keys at top level."""
        params = {}
        for k, v in self.data.items():
            key = kws.get(k, k)
            params[key] = v
        return self.new_like(params)

    # def rename(self, mapping: Mapping[Any, Hashable] | None = None, **kwargs) -> DocFiller:
    #     """
    #     New DocFiller with new names at top level.
    #     """

    #     if mapping is not None:
    #         m = dict(mapping)
    #     else:
    #         m = {}

    #     m = dict(m, **kwargs)

    #     data = self.data.copy()
    #     for old_name, v in m.items():
    #         data[]

    @cached.prop
    def params(self) -> AttributeDict:
        """An AttributeDict view of parameters."""
        return AttributeDict.from_dict(self.data, max_level=1)

    # HACK: cached.prop and mypy don't play nice with
    # returning a decorator from
    @property
    @cached.meth
    def _default_decorator(self) -> Callable[[F], F]:
        return doc_decorate(**self.params)

    def update(self, *args: Any, **kwargs: Any) -> DocFiller:
        """Update parameters"""
        new = self.new_like()
        new.data.update(*args, **kwargs)
        return new

    def assign(self, **kwargs: Any) -> DocFiller:
        """Assign new key/value pairs"""
        return self.update(**kwargs)

    def decorate(self, func: F) -> F:
        """
        Default decorator.

        This uses `self.params` and the decorated funciton docstring as a template.
        """
        return self._default_decorator(func)

    def __call__(
        self,
        *templates: Callable[..., Any] | str,
        _prepend: bool = False,
        **params: str,
    ) -> Callable[[F], F]:
        """
        General decorator.

        This should always be used in a callable manner.

        If want to call without any parameter use decorate()

        Parameters
        ----------
        *templates : callable
            docstrings to be used as templates.
        **params
            Extra parameters to be substituted.
        """
        ntemplates, nparams = len(templates), len(params)

        if ntemplates == nparams == 0 and not _prepend:
            return self.decorate
        elif nparams == 0:
            return doc_decorate(*templates, _prepend=_prepend, **self.params)
        else:
            return self.update(params)(*templates, _prepend=_prepend)

    # NOTE: This is dangerous.
    # if you pass a function as a template, but forget to explicitly pass it,
    # you overwrite the docstring for that function.  Just really confusing
    # def dec(self, *funcs, docstrings=None, **params) -> Callable[[F], F]:
    #     """
    #     General decorator.

    #     Parameters
    #     ----------
    #     *funcs : callable

    #     This should always be used in a callable manner.

    #     If want to call without any parameter use decorate()
    #     """

    #     nfuncs = len(funcs)

    #     if nfuncs == 0:
    #         func = None
    #     elif nfuncs == 1 and callable(funcs[0]):
    #         func = funcs[0]
    #     else:
    #         func = None    #         raise ValueError("Must call with zero or one functions.  If trying to set docstrings, be explicit")

    #     if docstrings is None:
    #         docstrings = ()
    #     elif callable(docstrings) or isinstance(docstrings, str):
    #         docstrings = (docstrings,)

    #     ndocstrings, nparams = (len(x) for x in (docstrings, params))

    #     if ndocstrings == nparams == 0:
    #         dec = self.default_decorator
    #     else:
    #         if nparams > 0:
    #             params = AttributeDict.from_dict({**self.data, **params}, max_level=1)
    #         else:
    #             params = self.params
    #         dec = doc_decorate(*docstrings, **params)

    #     if func:
    #         dec = dec(func)
    #     return dec

    # def __call__(self, *funcs, docstrings=None, **params) -> Callable[[F], F]:
    #     """
    #     Simplified decorator.

    #     Does not handle templates.
    #     """
    #     return self.dec(*funcs, docstrings=docstrings, **params)

    @classmethod
    def from_dict(
        cls,
        params: Mapping[str, Any],
        namespace: str | None = None,
        combine_keys: str | Sequence[str] | None = None,
        keep_keys: bool | str | Sequence[str] = True,
        key_map: Mapping[str, str] | Callable[[str], str] | None = None,
    ) -> DocFiller:
        """
        Create a Docfiller instance from a dictionary.

        Parameters
        ----------
        params : mapping
        namespace : str, optional
            Top level namespace for DocFiller.
        combine_keys : str, sequence of str, mapping, optional
            If str or sequence of str, Keys of ``params`` to at the top level.
            If mapping, should be of form {namespace: key(s)}

        keep_keys : str, sequence of str, bool
            If False, then don't keep any keys at top level.  This is useful with the ``combine_keys`` parameter.
            If True, keep all keys, regardless of combine_keys.
            If str or sequence of str, keep these keys in output.
        key_map : mapping or callable
            Function or mapping to new keys in resulting dict.

        Returns
        -------
        DocFiller
        """
        if not keep_keys:
            keep_keys = []
        elif keep_keys is True:
            keep_keys = [k for k in params]
        elif isinstance(keep_keys, str):
            keep_keys = [keep_keys]

        assert isinstance(keep_keys, Iterable)

        if combine_keys:
            if isinstance(combine_keys, str):
                combine_keys = [combine_keys]

            updated_params = {k: params[k] for k in keep_keys}

            # if isinstance(combine_keys, (list, tuple)):
            #     combine_keys = {'': combine_keys}

            # for k, v in combine_keys.items():

            #     if k in updated_params:
            #         updated_params =

            for k in combine_keys:
                updated_params.update(**params[k])

        else:
            updated_params = {k: params[k] for k in keep_keys}

        if key_map is not None:
            if callable(key_map):
                mapper = key_map
            elif isinstance(key_map, Mapping):

                def mapper(x: str, /) -> str:
                    return key_map[x]

            else:
                raise ValueError("unknown key_map {key_map}")

            updated_params = {mapper(k): updated_params[k] for k in updated_params}

        if namespace:
            updated_params = {namespace: updated_params}

        return cls(params=updated_params)

    @classmethod
    def from_docstring(
        cls,
        func_or_doc: Callable[..., Any] | str,
        namespace: str | None = None,
        combine_keys: str | Sequence[str] | None = None,
        key_char: str = "|",
        keep_keys: bool = True,
        key_map: Mapping[str, str] | Callable[[str], str] | None = None,
    ) -> DocFiller:
        """
        Create a Docfiller instance from a function or docstring.

        Parameters
        ----------
        func_or_doc : str or callable
            Docstring to parse to get parameters.
        namespace : str, optional
            Top level namespace for DocFiller.
        combine_keys : str, sequence of str, mapping, optional
            If str or sequence of str, Keys of ``params`` to at the top level.
            If mapping, should be of form {namespace: key(s)}
        key_char : str, default="|"
            Character to split names.  By default, for parameters, the key will be parsed from
            The docstring. If you want to override this, you can use
            `key | name : ....` in the definition (where `'|'` is the value of `key_char`).
        keep_keys : str, sequence of str, bool
            If False, then don't keep any keys at top level.  This is useful with the
            ``combine_keys`` parameter.
            If True, keep all keys, regardless of combine_keys.
            If str or sequence of str, keep these keys in output.
        key_map : mapping or callable
            Function or mapping to new keys in resulting dict.

        Returns
        -------
        DocFiller

        """
        params = _parse_docstring(
            func_or_doc=func_or_doc, key_char=key_char, expand=True
        )
        return cls.from_dict(
            params=params,
            namespace=namespace,
            combine_keys=combine_keys,
            keep_keys=keep_keys,
            key_map=key_map,
        )
