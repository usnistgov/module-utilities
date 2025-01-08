"""
Fill and share documentation (:mod:`~module_utilities.docfiller`)
=================================================================
"""

from __future__ import annotations

import inspect
from collections.abc import Iterable, Mapping
from textwrap import dedent, indent
from typing import (
    TYPE_CHECKING,
    NamedTuple,
    cast,
)

from . import cached
from ._doc import doc as _pd_doc
from .attributedict import AttributeDict
from .options import DOC_SUB
from .vendored.docscrape import NumpyDocString, Parameter

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from typing import (
        Any,
    )

    from .typing import F, NestedMap, NestedMapVal


def indent_docstring(
    docstring: str | Callable[..., Any], prefix: str | None = "+  "
) -> str:
    """Create indented docstring"""
    if callable(docstring):
        docstring = (docstring.__doc__ or "").strip()

    if prefix is not None:
        return indent(docstring, prefix)

    return docstring


# Factory method to create doc_decorate
def doc_decorate(
    *docstrings: str | Callable[..., Any] | None,
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


    Examples
    --------
    >>> @doc_decorate(type_="int")
    ... def func0(x, y):
    ...     '''
    ...     Parameters
    ...     ----------
    ...     x : {type_}
    ...         x parameter.
    ...     y : {type_}
    ...         y parameter.
    ...     Returns
    ...     -------
    ...     output : {type_}
    ...     '''
    ...     pass
    >>> print(indent_docstring(func0))
    +  Parameters
    +  ----------
    +  x : int
    +      x parameter.
    +  y : int
    +      y parameter.
    +  Returns
    +  -------
    +  output : int


    To inherit from a function/docstring, pass it:


    >>> @doc_decorate(func0, type_="float")
    ... def func1(x, y):
    ...     pass
    >>> print(indent_docstring(func1))
    +  Parameters
    +  ----------
    +  x : float
    +      x parameter.
    +  y : float
    +      y parameter.
    +  Returns
    +  -------
    +  output : float
    """
    if DOC_SUB:
        return _pd_doc(*docstrings, _prepend=_prepend, **params)

    def decorated(func: F) -> F:
        return func

    return decorated


def _build_param_docstring(
    name: str | None, ptype: str | None, desc: str | Sequence[str]
) -> str:
    """
    Create multiline documentation of single name, type, desc.

    Parameters
    ----------
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
    no_name = not name
    no_type = not ptype

    if no_name and no_type:
        msg = "must specify name or ptype"
        raise ValueError(msg)

    if no_type:
        s = f"{name}"
    elif no_name:
        s = f"{ptype}"
    else:
        s = f"{name} : {ptype}"

    if isinstance(desc, str):
        desc = [] if not desc else [desc]

    elif len(desc) == 1 and not desc[0]:
        desc = []

    if len(desc) > 0:
        desc = "\n    ".join(desc)
        s += f"\n    {desc}"
    return s


class TParameter(NamedTuple):
    """Interface to Parameters namedtuple in docscrape"""

    name: str
    type: str
    desc: str


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
        return "\n".join(cast("list[str]", params))

    out: dict[str, str] = {}
    for p in cast("list[TParameter]", params):
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

    >>> p2 = _parse_docstring(doc_string, expand=False)
    >>> print(p2["Parameters"])
    [Parameter(name='x', type='int', desc=['x parameter']), Parameter(name='y_alt | y', type='float', desc=['y parameter'])]


    """
    doc = inspect.getdoc(func_or_doc) if callable(func_or_doc) else func_or_doc

    parsed = cast(
        "dict[str, str | list[str] | list[Parameter]]",
        NumpyDocString(doc)._parsed_data,  # type: ignore[no-untyped-call] # pyright: ignore[reportUnknownMemberType, reportPrivateUsage]  # pylint: disable=protected-access
    )

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
        parsed_out = cast("dict[str, str | dict[str, str]]", parsed)
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
    ...     "a": {
    ...         "value": '''
    ...      a : int
    ...          A thing
    ...      '''
    ...     }
    ... }
    >>> print(data["a"]["value"])
    <BLANKLINE>
         a : int
             A thing
    <BLANKLINE>
    >>> data = dedent_recursive(data)
    >>> print(data["a"]["value"])
    a : int
        A thing
    """
    out: dict[str, NestedMapVal] = {}
    for k in data:
        v = data[k]
        v = dedent(v).strip() if isinstance(v, str) else dedent_recursive(v)
        out[k] = v
    return out


def _recursive_keys(data: NestedMap) -> list[str]:
    """
    Examples
    --------
    >>> d = {"a": "a", "b": {"c": "hello"}}
    >>> _recursive_keys(d)
    ['a', 'b.c']

    >>> d = {"a": 1}
    >>> _recursive_keys(d)
    Traceback (most recent call last):
    ...
    TypeError: unknown type <class 'int'>
    """
    keys: list[str] = []
    for k, v in data.items():
        if isinstance(v, Mapping):
            key_list = [f"{k}.{x}" for x in _recursive_keys(v)]
        elif isinstance(v, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            key_list = [k]
        else:
            msg = f"unknown type {type(v)}"
            raise TypeError(msg)

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


    Examples
    --------
    >>> docstring = '''
    ...     Parameters
    ...     ----------
    ...     x : int
    ...         x param
    ...     y : int
    ...         y param
    ...     z0 | z : int
    ...         z int param
    ...     z1 | z : float
    ...         z float param
    ...
    ...     Returns
    ...     -------
    ...     output0 | output : int
    ...         Integer output.
    ...     output1 | output : float
    ...         Float output
    ...     '''
    >>> d = DocFiller.from_docstring(docstring, combine_keys="parameters")
    >>> print(d.keys()[-4:])
    ['x', 'y', 'z0', 'z1']
    >>> @d.decorate
    ... def func(x, y, z):
    ...     '''
    ...     Parameters
    ...     ----------
    ...     {x}
    ...     {y}
    ...     {z0}
    ...     Returns
    ...     --------
    ...     {returns.output0}
    ...     '''
    ...     return x + y + z
    >>> print(indent_docstring(func))
    +  Parameters
    +  ----------
    +  x : int
    +      x param
    +  y : int
    +      y param
    +  z : int
    +      z int param
    +  Returns
    +  --------
    +  output : int
    +      Integer output.
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
        return f"{self.__class__.__name__}({self.data!r})"

    def new_like(self, data: NestedMap | None = None) -> DocFiller:
        """Create new object with optional data."""
        if data is None:
            data = self.data.copy()
        return type(self)(data)

    def __getitem__(self, key: str) -> DocFiller | str:
        val = self.data[key]
        if isinstance(val, Mapping):
            return self.new_like(val)

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
                msg = f"trying to combine key {k} with non-string value {d}"
                raise TypeError(msg)

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
        >>> d = DocFiller({"a0": "a0", "a1": "a1", "b": "b"})
        >>> dn = d.assign_keys(a="a0", c=["a0", "b"]).data
        >>> print(dn["a"])
        a0

        >>> print(dn["c"])
        a0
        b


        """
        new = self.new_like()
        for new_key, old_keys in kwargs.items():
            keys = [old_keys] if isinstance(old_keys, str) else list(old_keys)

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
        ...     name="x",
        ...     ptype="float",
        ...     desc='''
        ...     A parameter
        ...     with multiple levels
        ...     ''',
        ... )
        >>> print(dn["x"])
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
                msg = f"level {name} is not a dict"
                raise TypeError(msg)

            for k, v in d.items():
                new.data[k] = v
        return new

    def rename_levels(self, **kws: str) -> DocFiller:
        """Rename a keys at top level."""
        params: dict[str, Any] = {}
        for k, v in self.data.items():
            key = kws.get(k, k)
            params[key] = v
        return self.new_like(params)

    @cached.prop
    def params(self) -> AttributeDict:
        """An AttributeDict view of parameters."""
        return AttributeDict.from_dict(self.data, max_level=1)

    @cached.prop
    def _default_decorator(self) -> Callable[[F], F]:
        return doc_decorate(**self.params)  # pylint: disable=not-a-mapping)

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

        This uses `self.params` and the decorated function docstring as a template.
        If need to pass parameters, use self.__call__


        See Also
        --------
        __call__


        """
        return self._default_decorator(func)  # pylint: disable=too-many-function-args

    def __call__(
        self,
        *templates: Callable[..., Any] | str,
        _prepend: bool = False,
        **params: str,
    ) -> Callable[[F], F]:
        """
        Factory function to create docfiller decorator.

        This should always be used in a callable manner.

        If want to call without any parameter use decorate()

        Parameters
        ----------
        *templates : callable
            docstrings to be used as templates.
        _prepend : bool, default=False
            If `True`, then prepend `templates` with docstring of decorated function.
            Otherwise, append to end.
        **params
            Extra parameters to be substituted.


        Example
        -------
        Using the default decorator


        >>> d = DocFiller({"x": "hello", "y": "there"})
        >>> @d.decorate
        ... def func():
        ...     '''
        ...     A function with  x={x} and y={y}
        ...     '''
        ...     pass
        >>> print(indent_docstring(func))
        +  A function with  x=hello and y=there


        Using call without args


        >>> @d()
        ... def func1():
        ...     '''
        ...     A new function with x={x} and y={y}
        ...     '''
        ...     pass
        >>> print(indent_docstring(func1))
        +  A new function with x=hello and y=there

        Using call with args. This inherits from passed template


        >>> @d(func, x="new_x")
        ... def func2():
        ...     pass
        >>> print(indent_docstring(func2))
        +  A function with  x=new_x and y=there
        """
        ntemplates, nparams = len(templates), len(params)

        if ntemplates == nparams == 0 and not _prepend:
            return self.decorate
        if nparams == 0:
            return doc_decorate(*templates, _prepend=_prepend, **self.params)  # pylint: disable=not-a-mapping

        return self.update(params)(*templates, _prepend=_prepend)

    def inherit(
        self,
        template: Callable[..., Any],
        _prepend: bool = False,
        **params: str,
    ) -> Callable[[F], F]:
        """
        Factor function to create decorator.

        Use combination of docstring_inheritance.inherit_numpy_docstring and
        DocFiller.

        Parameters
        ----------
        template : callable
            Template method to inherit from.
        _prepend : bool, default=False
            Prepend parameter.
        **params :
            Extra parameter specifications.

        Returns
        -------
        decorator : callable
            Decorator

        See Also
        --------
        ~module_utilities.docinherit.doc_inherit
        """
        from . import docinherit

        docfiller = self.update(params)

        def decorator(func: F) -> F:
            @docfiller(template)
            def dummy() -> None:  # pragma: no cover
                pass

            func = docfiller(_prepend=_prepend)(func)

            return docinherit.doc_inherit(parent=dummy)(func)

        return decorator

    def factory_from_parent(
        self,
        cls: type,
    ) -> Callable[..., Callable[[F], F]]:
        """
        Interface to docinherit.factory_docfiller_from_parent.

        Parameters
        ----------
        cls : type
            Class to inherit from.

        See Also
        --------
        ~module_utilities.docinherit.factory_docfiller_from_parent
        """
        from . import docinherit

        return docinherit.factory_docfiller_from_parent(cls, self)

    def factory_inherit_from_parent(
        self,
        cls: type,
    ) -> Callable[..., Callable[[F], F]]:
        """
        Interface to docinherit.factory_docfiller_inherit_from_parent.

        Parameters
        ----------
        cls : type
            Class to inherit from

        See Also
        --------
        ~module_utilities.docinherit.factory_docfiller_inherit_from_parent
        """
        from . import docinherit

        return docinherit.factory_docfiller_inherit_from_parent(cls, self)

    @classmethod
    def from_dict(  # noqa: C901
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
            keep_keys = list(params)
        elif isinstance(keep_keys, str):
            keep_keys = [keep_keys]

        if not isinstance(keep_keys, Iterable):  # pyright: ignore[reportUnnecessaryIsInstance]  # pragma: no cover
            msg = f"keep_keys must be iterable, not {type(keep_keys)=}"
            raise TypeError(msg)

        if combine_keys:
            if isinstance(combine_keys, str):
                combine_keys = [combine_keys]

            updated_params = {k: params[k] for k in keep_keys}

            for k in combine_keys:
                updated_params.update(**params[k])

        else:
            updated_params = {k: params[k] for k in keep_keys}

        if key_map is None:
            pass
        elif callable(key_map):
            updated_params = {key_map(k): v for k, v in updated_params.items()}
        else:
            updated_params = {key_map[k]: v for k, v in updated_params.items()}

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
        keep_keys: bool | str | Sequence[str] = True,
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
