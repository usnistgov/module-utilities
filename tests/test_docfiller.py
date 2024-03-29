# mypy: disable-error-code="no-untyped-def"
from __future__ import annotations
from textwrap import dedent
from typing import cast

# from typing import TYPE_CHECKING
# from typing_extensions import reveal_type

import pytest

from module_utilities import docfiller
from module_utilities.docfiller import DocFiller, dedent_recursive

# just testing on doc routine:


# --- simple (coverage filler) tests ---------------------------------------------------


def test_append():
    def func():
        """Hello"""

    @docfiller.doc_decorate(func, x="there")
    def func1():
        """{x}"""

    assert func1.__doc__.strip() == "Hellothere"  # type: ignore

    @docfiller.doc_decorate(func, x="some", _prepend=True)
    def func2():
        """Yell"""

    assert func2.__doc__ == "YellHello"

    def func_none():
        pass

    func_none.__doc__ = None

    @docfiller.doc_decorate(None, x="there")
    def func3():
        """Hello {x}"""
        pass

    assert func3.__doc__ == "Hello there"

    docfiller.DOC_SUB = False  # type: ignore

    @docfiller.doc_decorate(func1, x="hello")
    def func4a():
        """{x}"""

    docfiller.DOC_SUB = True  # type: ignore

    assert func4a.__doc__ == "{x}"


def test_indent_docstring():
    assert docfiller.indent_docstring("hello", prefix=" ") == " hello"
    assert docfiller.indent_docstring("hello", prefix=None) == "hello"


def test_build_params_docstring():
    with pytest.raises(ValueError):
        s = docfiller._build_param_docstring(name="", ptype="", desc=["hello"])

    s = docfiller._build_param_docstring(name="hello", ptype=None, desc="stuff")

    assert (
        s
        == dedent(
            """
    hello
        stuff
    """
        ).strip()
    )

    s = docfiller._build_param_docstring(name="hello", ptype=None, desc="")

    assert s == "hello"

    s = docfiller._build_param_docstring(name="hello", ptype=None, desc=[""])

    assert s == "hello"


def test_params_to_string():
    s = docfiller._params_to_string("hello")
    assert s == "hello"


def test_func_or_doc():
    def template():
        """
        Parameters
        ----------
        x : int
        """

    d = DocFiller.from_docstring(template, combine_keys="parameters")

    @d.decorate
    def func():
        """{x}"""

    assert func.__doc__ == "x : int"


def test_docfiller_creation():
    d = DocFiller([("x", "hello")])  # type: ignore

    @d.decorate
    def func():
        "{x}"

    assert func.__doc__ == "hello"

    assert repr(d) == "DocFiller({'x': 'hello'})"


def test_DocFiller_getitem():
    d = DocFiller.from_docstring(
        """
    Parameters
    ----------
    x : int
    y : float
    """,
        keep_keys="parameters",
    )

    dd = cast(DocFiller, d["parameters"])

    @dd.decorate
    def func():
        """{x}"""

    assert func.__doc__ == "x : int"

    @dd.decorate
    def func1():
        """
        {x}
        {y}
        """

    ddd = dd.assign_combined_key("z", ["x", "y"])

    @ddd.decorate
    def func2():
        """
        {z}
        """

    assert func1.__doc__ == func2.__doc__

    with pytest.raises(ValueError):
        ddd = d.assign_combined_key("zz", ["parameters"])

    d = DocFiller.from_docstring(
        """
    Parameters
    ----------
    x : int
    y : float
    """,
        keep_keys=False,
        combine_keys="parameters",
        key_map=lambda x: "hello_" + x,
    )

    @d.decorate
    def func3():
        """{hello_x}"""

    assert func3.__doc__ == "x : int"

    d = DocFiller.from_docstring(
        """
    Parameters
    ----------
    x : int
    y : float
    """,
        keep_keys=False,
        combine_keys="parameters",
        key_map={"x": "hello_x", "y": "hello_y"},
        namespace="top",
    )

    @d.decorate
    def func4():
        """{top.hello_x}"""

    assert func4.__doc__ == "x : int"


@pytest.fixture
def params():
    return dedent_recursive(
        dict(
            summary="A thing",
            a="""
            a : int
                A Parameter
        """,
            b="""
        b : float
            B Parameter
        """,
            output="""
        output : float
        """,
        )
    )


@pytest.fixture
def expected():
    return dedent(
        """
    A thing

    Parameters
    ----------
    a : int
        A Parameter
    b : float
        B Parameter

    Returns
    -------
    output : float
    """
    )


@pytest.fixture
def template(params):
    @docfiller.doc_decorate(**params)
    def func(*args, **kwargs):
        """
        {summary}

        Parameters
        ----------
        {a}
        {b}

        Returns
        -------
        {output}
        """

    return func


# Basic doc decorator
def test_dedent_recursive(params):
    assert params["a"] == "a : int\n    A Parameter"


def test_doc(template, expected):
    assert template.__doc__ == expected


def test_doc_from_template(template, params, expected):
    @docfiller.doc_decorate(template, **params)
    def func():
        pass

    assert func.__doc__ == expected


def test_doc_from_docstring(template, params, expected):
    @docfiller.doc_decorate(template.__doc__, **params)
    def func():
        pass

    assert func.__doc__ == expected


def test_DocFiller(template, params, expected):
    d = docfiller.DocFiller()

    @d(template, **params)
    def func():
        pass

    assert func.__doc__ == expected

    # @d.update(**params).dec(template)
    # NOTE: can't do above in python 3.8
    dd = d.update(**params)

    @dd(template)
    def func2():
        pass

    assert func2.__doc__ == expected

    # @d.update(params).dec(template)
    dd = d.update(params)

    @dd(template)
    def func3():
        pass

    assert func3.__doc__ == expected

    d = docfiller.DocFiller.from_dict(params)

    @d(template)
    def func4():
        pass

    assert func4.__doc__ == expected


def test_DocFiller_docstring():
    docstring = """
    A summary line

    An extended summary

    Parameters
    ----------
    a : int
        A parameter
    b : float
        B parameter
    c : other
        C parameter

    Returns
    -------
    float
        A floating return
    """

    d = DocFiller.from_docstring(docstring, combine_keys="parameters")

    docstring = dedent(docstring)

    @d()
    def function():
        """
        {summary}

        {extended_summary}

        Parameters
        ----------
        {a}
        {b}
        {c}

        Returns
        -------
        {returns[:]}
        """

    assert docstring == function.__doc__

    @d.decorate
    def function2():
        """
        {summary}

        {extended_summary}

        Parameters
        ----------
        {a}
        {b}
        {c}

        Returns
        -------
        {returns[:]}
        """

    assert docstring == function2.__doc__
    # update
    dd = d.update(
        hello="""
        hello : int
            Hello param
        """,
        there="""
        there : float
            There param
        """,
    ).dedent()

    @dd.decorate
    def function3():
        """
        {summary}

        Parameters
        ----------
        {a}
        {b}
        {hello}
        {there}
        """

    expected = dedent(
        """
    A summary line

    Parameters
    ----------
    a : int
        A parameter
    b : float
        B parameter
    hello : int
        Hello param
    there : float
        There param
    """
    )
    assert function3.__doc__ == expected

    d2 = docfiller.DocFiller.from_docstring(
        """
        Parameters
        ----------
        hello : int
            Hello param
        there : float
            There param
        """,
        combine_keys="parameters",
        keep_keys=False,
    )

    dd = d.append(d2)

    @dd(function3)
    def function4():
        pass

    assert function4.__doc__ == expected


def test_DocFiller_namespace() -> None:
    s0 = """
    Parameters
    ----------
    a : int
        A param
    b : int
        B param

    Returns
    -------
    out : int
        O param
    """

    d0 = docfiller.DocFiller.from_docstring(s0)

    s1 = """
    Parameters
    ----------
    a : float
        AA param
    b_alt | b : float
        BB param

    Returns
    -------
    out : float
        OO param
    """

    d0 = docfiller.DocFiller.from_docstring(s0)
    d1 = docfiller.DocFiller.from_docstring(s1)

    dd0 = d0.insert_level("a").append(d1.insert_level("b"))

    dd1 = docfiller.DocFiller.concat(a=d0, b=d1, c={"type_": "int"})

    assert dd1["c"]["type_"] == "int"  # type: ignore

    expected = dedent(
        """
        Parameters
        ----------
        a : int
            A param
        b : float
            BB param

        Returns
        -------
        out : float
            OO param
        """
    )

    for dd in [dd0, dd1]:

        @dd.decorate
        def func():
            """
            Parameters
            ----------
            {a.parameters.a}
            {b.parameters.b_alt}

            Returns
            -------
            {b.returns.out}
            """

            pass

        assert func.__doc__ == expected

    with pytest.raises(ValueError):
        d0.assign(x="hello").levels_to_top("x")

    dd0 = (
        d0.rename_levels(parameters="p", returns="r")
        .levels_to_top("p", "r")
        .insert_level("a")
    )

    dd1 = (
        d1.rename_levels(parameters="p", returns="r")
        .levels_to_top("p", "r")
        .insert_level("b")
    )

    dd = dd0.append(dd1)

    @dd.decorate
    def func2(a: int, b: int) -> tuple[int, int]:
        """
        Parameters
        ----------
        {a.p.a}
        {b.p.b_alt}

        Returns
        -------
        {b.r.out}
        """

        return a, b

    assert func2.__doc__ == expected

    assert func2(1, 1) == (1, 1)


def test_assign_key():
    d = DocFiller.from_docstring(
        """
        Parameters
        ----------
        x_float | x : float
            x float
        x_array | x : array-like
            x array
        y : int
            y val
        """,
        combine_keys="parameters",
    )

    dd = d.assign_keys(x="x_float")

    @dd.decorate
    def test0():
        """
        Parameters
        ----------
        {x}
        """

    expected = dedent(
        """
        Parameters
        ----------
        x : float
            x float
        """
    )

    assert test0.__doc__ == expected

    dd = d.assign_keys(x="x_array")

    @dd.decorate
    def test1():
        """
        Parameters
        ----------
        {x}
        """

    expected = dedent(
        """
        Parameters
        ----------
        x : array-like
            x array
        """
    )

    assert test1.__doc__ == expected

    dd = d.assign_keys(x=["x_array", "y"])

    @dd.decorate
    def test2():
        """
        Parameters
        ----------
        {x}
        """

    expected = dedent(
        """
        Parameters
        ----------
        x : array-like
            x array
        y : int
            y val
        """
    )

    assert test2.__doc__ == expected


def test_DocFiller_assign_param():
    expected = dedent(
        """
    A summary

    A longer summary

    Parameters
    ----------
    x : float
        x param
        With an extra line
    y : int
        y param
    z : float
    """
    )

    d = DocFiller()

    dd = (
        d.assign_param(
            "x",
            ptype="float",
            desc="""
            x param
            With an extra line
            """,
        )
        .assign_param("y", ptype="int", desc="y param")
        .assign_param("z", ptype="float")
    )

    @dd()
    def func():
        """
        A summary

        A longer summary

        Parameters
        ----------
        {x}
        {y}
        {z}
        """
        pass

    assert func.__doc__ == expected


def test_DocFiller_on_class():
    expected = """
    A summary

    A longer summary

    Parameters
    ----------
    x : float
        x param
        some other stuff
    y : float
        y param

    Returns
    -------
    out : float
        output
    """

    expected = dedent(expected)

    d = DocFiller.from_docstring(expected, combine_keys="parameters")

    @d()
    class hello:
        """
        {summary}

        {extended_summary}

        Parameters
        ----------
        {x}
        {y}

        Returns
        -------
        {returns.out}
        """

    assert hello.__doc__ == expected

    @d(hello)
    class hello2(hello):
        pass

    assert hello.__doc__ == expected


def test_prepend():
    expected = """
    A summary

    A longer summary

    Parameters
    ----------
    x : float
        x param
        some other stuff
    y : float
        y param

    Returns
    -------
    out : float
        output
    """

    expected = dedent(expected)

    d = DocFiller.from_docstring(expected, combine_keys="parameters")

    def template(x: float, y: float) -> float:
        """
        {summary}

        {extended_summary}

        Parameters
        ----------
        {x}
        {y}
        """
        return x + y

    # reveal_type(template)
    # reveal_type(template(1.0, 2.0))

    @d(template)
    def hello(x: float, y: float) -> float:
        """
        Returns
        -------
        {returns.out}
        """
        return x + y

    assert hello.__doc__ == expected

    # reveal_type(hello)
    # reveal_type(hello(1., 2.))

    # prepend
    @d(template, _prepend=True)
    def there():
        """
        Returns
        -------
        {returns.out}
        """
        pass

    expected = """
    Returns
    -------
    out : float
        output

    A summary

    A longer summary

    Parameters
    ----------
    x : float
        x param
        some other stuff
    y : float
        y param
    """

    assert dedent(expected) == there.__doc__
