# mypy: disable-error-code="no-untyped-def"
# pylint: disable=protected-access
from __future__ import annotations

from textwrap import dedent
from typing import cast

import pytest

from module_utilities import docfiller
from module_utilities.docfiller import DocFiller, dedent_recursive

# just testing on doc routine:


# --- simple (coverage filler) tests ---------------------------------------------------


def test_doc_decorate_simple() -> None:
    def func():
        """
        Thing

        Parameters
        ----------
        {a}
        """

    @docfiller.doc_decorate(func, a="there")
    def other():
        pass

    @docfiller.doc_decorate(func.__doc__, a="there")
    def other2():
        pass

    @docfiller.doc_decorate(None, func.__doc__, a="there")
    def other3():
        pass

    @docfiller.doc_decorate(other, a="there")
    def there():
        pass

    @docfiller.doc_decorate(a="there")
    def another():
        """
        Thing

        Parameters
        ----------
        {a}
        """

    expected = dedent(
        """
    Thing

    Parameters
    ----------
    there
    """
    ).strip()

    for f in [other, other2, other3, there, another]:
        assert dedent(f.__doc__).strip() == expected  # type: ignore[arg-type]

    with pytest.raises(ValueError):  # noqa: PT011

        @docfiller.doc_decorate(1, a="there")  # type: ignore[arg-type]
        def bad_func():
            pass


def test_append() -> None:
    def func() -> None:
        """Hello"""

    @docfiller.doc_decorate(func, x="there")
    def func1() -> None:
        """{x}"""

    assert func1.__doc__.strip() == "Hellothere"  # type: ignore[union-attr]

    @docfiller.doc_decorate(func, x="some", _prepend=True)
    def func2() -> None:
        """Yell"""

    assert func2.__doc__ == "YellHello"

    def func_none() -> None:
        pass

    func_none.__doc__ = None

    @docfiller.doc_decorate(None, x="there")
    def func3() -> None:
        """Hello {x}"""

    assert func3.__doc__ == "Hello there"

    docfiller.DOC_SUB = False  # type: ignore[attr-defined]

    @docfiller.doc_decorate(func1, x="hello")
    def func4a() -> None:
        """{x}"""

    docfiller.DOC_SUB = True  # type: ignore[attr-defined]

    assert func4a.__doc__ == "{x}"


def test_indent_docstring() -> None:
    assert docfiller.indent_docstring("hello", prefix=" ") == " hello"
    assert docfiller.indent_docstring("hello", prefix=None) == "hello"


def test_build_params_docstring() -> None:
    with pytest.raises(ValueError):  # noqa: PT011
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


def test_params_to_string() -> None:
    s = docfiller._params_to_string("hello")
    assert s == "hello"


def test_func_or_doc() -> None:
    def template() -> None:
        """
        Parameters
        ----------
        x : int
        """

    d = DocFiller.from_docstring(template, combine_keys="parameters")

    @d.decorate
    def func() -> None:
        """{x}"""

    assert func.__doc__ == "x : int"


def test_docfiller_creation() -> None:
    d = DocFiller([("x", "hello")])  # type: ignore[arg-type]

    @d.decorate
    def func() -> None:
        """{x}"""

    assert func.__doc__ == "hello"

    assert repr(d) == "DocFiller({'x': 'hello'})"


def test_docfiller_getitem() -> None:
    d = DocFiller.from_docstring(
        """
    Parameters
    ----------
    x : int
    y : float
    """,
        keep_keys="parameters",
    )

    dd = cast("DocFiller", d["parameters"])

    @dd.decorate
    def func() -> None:
        """{x}"""

    assert func.__doc__ == "x : int"

    @dd.decorate
    def func1() -> None:
        """
        {x}
        {y}
        """

    ddd = dd.assign_combined_key("z", ["x", "y"])

    @ddd.decorate
    def func2() -> None:
        """{z}"""

    assert func1.__doc__.strip() == func2.__doc__  # type: ignore[union-attr]

    with pytest.raises(TypeError):
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
    def func3() -> None:
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
    def func4() -> None:
        """{top.hello_x}"""

    assert func4.__doc__ == "x : int"


@pytest.fixture
def params():
    return dedent_recursive(
        {
            "summary": "A thing",
            "a": """
            a : int
                A Parameter
        """,
            "b": """
        b : float
            B Parameter
        """,
            "output": """
        output : float
        """,
        }
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
    def func(*args, **kwargs) -> None:
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
def test_dedent_recursive(params) -> None:
    assert params["a"] == "a : int\n    A Parameter"


def test_doc(template, expected) -> None:
    assert template.__doc__ == expected


def test_doc_from_template(template, params, expected) -> None:
    @docfiller.doc_decorate(template, **params)
    def func() -> None:
        pass

    assert func.__doc__ == expected


def test_doc_from_docstring(template, params, expected) -> None:
    @docfiller.doc_decorate(template.__doc__, **params)
    def func() -> None:
        pass

    assert func.__doc__ == expected


def test_docfiller(template, params, expected) -> None:
    d = docfiller.DocFiller()

    @d(template, **params)
    def func() -> None:
        pass

    assert func.__doc__ == expected

    # @d.update(**params).dec(template)
    # NOTE: can't do above in python 3.8
    dd = d.update(**params)

    @dd(template)
    def func2() -> None:
        pass

    assert func2.__doc__ == expected

    # @d.update(params).dec(template)
    dd = d.update(params)

    @dd(template)
    def func3() -> None:
        pass

    assert func3.__doc__ == expected

    d = docfiller.DocFiller.from_dict(params)

    @d(template)
    def func4() -> None:
        pass

    assert func4.__doc__ == expected

    # convoluted way to test from_dict with combine_keys
    data = docfiller.DocFiller.from_docstring(expected).data

    d = docfiller.DocFiller.from_dict(data, combine_keys=["parameters", "returns"])

    @d(template)
    def func5() -> None:
        pass

    assert func5.__doc__ == expected


def test_docfiller_docstring() -> None:
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
    def function() -> None:
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
    def function2() -> None:
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
    def function3() -> None:
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
    def function4() -> None:
        pass

    assert function4.__doc__ == expected


def test_docfiller_namespace() -> None:
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

    assert dd1["c"]["type_"] == "int"  # type: ignore[index]

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

        @dd.decorate  # pylint: disable=cell-var-from-loop
        def func() -> None:
            """
            Parameters
            ----------
            {a.parameters.a}
            {b.parameters.b_alt}

            Returns
            -------
            {b.returns.out}
            """

        assert func.__doc__ == expected

    with pytest.raises(TypeError):
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


def test_assign_key() -> None:
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
    def test0() -> None:
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
    def test1() -> None:
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
    def test2() -> None:
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


def test_docfiller_assign_param() -> None:
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
    a : int
        Another
        parameter
    """
    )

    d = DocFiller()

    dd = (
        d.assign_param(
            name="x",
            ptype="float",
            desc="""
            x param
            With an extra line
            """,
            key="x_thing",
        )
        .assign_param("y", ptype="int", desc="y param")
        .assign_param("z", ptype="float")
        .assign_param("a", ptype="int", desc=["Another", "parameter"])
    )

    @dd()
    def func() -> None:
        """
        A summary

        A longer summary

        Parameters
        ----------
        {x_thing}
        {y}
        {z}
        {a}
        """

    assert func.__doc__ == expected


def test_docfiller_on_class() -> None:
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
    class hello2(hello):  # pylint: disable=missing-class-docstring,unused-variable
        pass

    assert hello.__doc__ == expected


def test_prepend() -> None:
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

    @d(template)
    def hello(x: float, y: float) -> float:
        """
        Returns
        -------
        {returns.out}
        """
        return x + y

    assert hello.__doc__ == expected

    # prepend
    @d(template, _prepend=True)
    def there() -> None:
        """
        Returns
        -------
        {returns.out}
        """

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
