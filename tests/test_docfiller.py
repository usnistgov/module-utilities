from textwrap import dedent

import pytest

from module_utilities import docfiller
from module_utilities.docfiller import DocFiller, dedent_recursive

# just testing on doc routine:


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
    def func():
        pass

    assert func.__doc__ == expected

    # @d.update(params).dec(template)
    dd = d.update(params)

    @dd(template)
    def func():
        pass

    assert func.__doc__ == expected

    d = docfiller.DocFiller.from_dict(params)

    @d(template)
    def func():
        pass

    assert func.__doc__ == expected


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
    def function():
        """
        {summary}

        Parameters
        ----------
        {a}
        {b}
        {hello}
        {there}
        """

    expected = docfiller.dedent(
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
    assert function.__doc__ == expected

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

    @dd(function)
    def func2():
        pass

    assert func2.__doc__ == expected


def test_DocFiller_namespace():
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

    dd1 = docfiller.DocFiller.concat(a=d0, b=d1)

    expected = docfiller.dedent(
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
    def func():
        """
        Parameters
        ----------
        {a.p.a}
        {b.p.b_alt}

        Returns
        -------
        {b.r.out}
        """

        pass

    assert func.__doc__ == expected
