# pyright: strict
from __future__ import annotations

from textwrap import dedent
from typing import Any, Callable

import pytest

from module_utilities import docinherit
from module_utilities.docfiller import DocFiller

pytestmark = [
    pytest.mark.inherit,
    pytest.mark.skipif(
        not docinherit.HAS_INHERIT, reason="docstring_inheritance not installed"
    ),
]


@pytest.fixture(scope="module")
def docstring_template() -> str:
    return """\
    Parameters
    ----------
    x : {type_}
        x parameter.
    y : {type_}
        y parameter.
    z : {type_}
        z parameter.
    """


@pytest.fixture(scope="module")
def docfiller_int(docstring_template: str) -> DocFiller:
    return DocFiller.from_docstring(
        docstring_template.format(type_="int"), combine_keys="parameters"
    ).assign(klass="int")


@pytest.fixture(scope="module")
def docfiller_float(docstring_template: str) -> DocFiller:
    return DocFiller.from_docstring(
        docstring_template.format(type_="float"), combine_keys="parameters"
    ).assign(klass="float")


@pytest.fixture(scope="module")
def docfiller_str(docstring_template: str) -> DocFiller:
    return DocFiller.from_docstring(
        docstring_template.format(type_="str"), combine_keys="parameters"
    ).assign(klass="str")


# --- testing inherit -------------------------------------------------------------------


def test_basic() -> None:
    def func(x: int) -> int:
        """
        Parameters
        ----------
        x : int
        """
        return x

    @docinherit.doc_inherit(func.__doc__ or "")
    def func2(x: int, y: float) -> float:
        """
        Parameters
        ----------
        y : float
        """
        return x + y

    assert (func2.__doc__ or "").strip() == dedent(
        """
    Parameters
    ----------
    x : int
    y : float
    """
    ).strip()

    docinherit.DOC_SUB = False  # type: ignore[attr-defined]

    @docinherit.doc_inherit(func)
    def func3(x: int, y: float) -> float:
        """
        Parameters
        ----------
        y : float
        """
        return x + y

    docinherit.DOC_SUB = True  # type: ignore[attr-defined]
    assert (
        dedent(func3.__doc__ or "").strip()
        == dedent(
            """
    Parameters
    ----------
    y : float
    """
        ).strip()
    )


@pytest.fixture(scope="module")
def example_func(docfiller_int: DocFiller) -> Callable[[int, int], int]:
    @docfiller_int.decorate
    def func(x: int, y: int) -> int:
        """
        Test1

        Parameters
        ----------
        {x}
        {y}

        Returns
        -------
        output : {klass}
            Output parameters.
        """
        return x + y

    return func


@pytest.fixture(scope="module")
def expected_func_template() -> str:
    return dedent(
        """
    {summary}

    Parameters
    ----------
    x : {type_}
        x parameter.
    y : {type_}
        y parameter.

    Returns
    -------
    output : {type_}
        Output parameters.
    """
    )


def compare_func(func: Callable[..., Any], template: str, /, **kwargs: str) -> None:
    assert func.__doc__.strip() == template.format(**kwargs).strip()  # type: ignore[union-attr]


def test_func_1(example_func: Callable[..., Any], expected_func_template: str) -> None:
    compare_func(example_func, expected_func_template, summary="Test1", type_="int")


def test_func_2(
    example_func: Callable[..., Any],
    expected_func_template: str,
    docfiller_float: DocFiller,
) -> None:
    @docfiller_float(example_func)
    def func(x: float, y: float) -> float:
        return x + y

    compare_func(func, expected_func_template, summary="Test1", type_="float")

    @docfiller_float.inherit(example_func)
    def func2(x: float, y: float) -> float:
        return x + y

    compare_func(func2, expected_func_template, summary="Test1", type_="float")

    # note that parameter not in args will get ignored
    @docfiller_float.inherit(example_func)
    def func3(x: float, y: float) -> float:
        """
        Parameters
        ----------
        z : int
            z thing
        """
        return x + y

    compare_func(func3, expected_func_template, summary="Test1", type_="float")


def test_func_3(
    example_func: Callable[..., Any],
    expected_func_template: str,
    docfiller_float: DocFiller,
) -> None:
    # Also, if parameter not in args, it will get ignored
    @docfiller_float(example_func, notes="hello")
    def func(x: float, y: float) -> float:
        """
        Notes
        -----
        {notes}
        """
        return x + y

    template = expected_func_template + dedent(
        """
    Notes
    -----
    hello
    """
    )

    compare_func(func, template, summary="Test1", type_="float")


def test_func_3a(
    example_func: Callable[..., Any],
    expected_func_template: str,
    docfiller_float: DocFiller,
) -> None:
    @docfiller_float(example_func, notes="hello")
    def func(x: float, y: float) -> float:
        """
        Notes
        -----
        {notes}
        """
        return x + y

    template = expected_func_template + dedent(
        """
    Notes
    -----
    hello
    """
    )

    compare_func(func, template, summary="Test1", type_="float")


@pytest.fixture(scope="module")
def expected_func_template_z() -> str:
    return dedent(
        """
    {summary}

    Parameters
    ----------
    x : {type_}
        x parameter.
    y : {type_}
        y parameter.
    z : {type_}
        z parameter.

    Returns
    -------
    new_output : {type_}
        New output
    """
    )


def test_func_4(
    example_func: Callable[..., Any],
    expected_func_template_z: str,
    docfiller_float: DocFiller,
) -> None:
    # Note: there's a bug with custom_inherit.  Need the extra space to make indentation work
    @docfiller_float.inherit(example_func)
    def func(x: float, y: float, z: int) -> float:
        """
        Testz

        Parameters
        ----------
        z : float
            z parameter.

        Returns
        -------
        new_output : float
            New output
        """
        return x + y + z

    compare_func(func, expected_func_template_z, summary="Testz", type_="float")


def test_func_5(
    example_func: Callable[..., Any],
    expected_func_template_z: str,
    docfiller_float: DocFiller,
) -> None:
    d = (
        docfiller_float.assign(type_="float")
        .assign_param("z", "float", "z parameter.")
        .inherit(example_func)
    )

    @d
    def func(x: float, y: float, z: int) -> float:
        """
        Testz

        Parameters
        ----------
        {z}

        Returns
        -------
        new_output : {type_}
            New output
        """
        return x + y + z

    compare_func(func, expected_func_template_z, summary="Testz", type_="float")

    d = docfiller_float.assign_param("z", "float", "z parameter.").inherit(
        example_func, type_="float"
    )

    @d
    def func2(x: float, y: float, z: int) -> float:
        """
        Testz

        Parameters
        ----------
        {z}

        Returns
        -------
        new_output : {type_}
            New output
        """
        return x + y + z

    compare_func(func2, expected_func_template_z, summary="Testz", type_="float")

    # Note that if the parameter is missing, will get the following:
    expected_template = dedent(
        """
    {summary}

    Parameters
    ----------
    x : {type_}
        x parameter.
    y : {type_}
        y parameter.
    z
        The description is missing.

    Returns
    -------
    new_output : {type_}
        New output
    """
    )

    d = docfiller_float.assign(type_="float").inherit(example_func)

    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        @d
        def func3(x: float, y: float, z: int) -> float:
            """
            Testz

            Returns
            -------
            new_output : {type_}
                New output
            """
            return x + y + z

        compare_func(func3, expected_template, summary="Testz", type_="float")


# --- Class filling --------------------------------------------------------------------
@pytest.fixture(scope="module")
def example_class(docfiller_int: DocFiller) -> Any:
    # @docfiller_int.decorate

    class ExampleClass:
        """
        A class to do a thing

        Parameters
        ----------
        {x}
        {y}
        """

        def __init__(self, x: int, y: int) -> None:
            pass

        @docfiller_int.decorate
        def meth(self, z: int) -> int:
            """
            A meth

            Parameters
            ----------
            {z}
            """
            return z

        @docfiller_int.decorate
        def meth2(self, z: int) -> int:
            """
            A meth2

            Parameters
            ----------
            {z}
            """
            return z

        def meth3(self, z: int) -> int:
            """
            Parameters
            ----------
            x : float
                A parameter for stuff.
            """
            return z

    return docfiller_int.decorate(ExampleClass)


@pytest.fixture(scope="module")
def expected_class() -> str:
    return dedent(
        """
    {summary}

    Parameters
    ----------
    x : {type_}
        x parameter.
    y : {type_}
        y parameter.
    """
    )


@pytest.fixture(scope="module")
def expected_meth() -> str:
    return dedent(
        """
    {summary}

    Parameters
    ----------
    z : {type_}
        z parameter.
    """
    )


def compare_docs(doc: str | Callable[..., Any] | None, expected: str | None) -> None:
    if callable(doc):
        doc = doc.__doc__
    if doc is None:
        doc = ""

    expected = expected or ""

    a = doc.strip()
    b = dedent(expected).strip()
    assert a == b


def test_example_class(
    example_class: Any, expected_class: str, expected_meth: str
) -> None:
    compare_docs(
        example_class.__doc__,
        expected_class.format(type_="int", summary="A class to do a thing"),
    )
    compare_docs(
        example_class.meth.__doc__, expected_meth.format(type_="int", summary="A meth")
    )
    compare_docs(
        example_class.meth2.__doc__,
        expected_meth.format(type_="int", summary="A meth2"),
    )


def test_inherit_2(
    example_class: Any,
    docfiller_float: DocFiller,
    expected_class: str,
    expected_meth: str,
) -> None:
    @docfiller_float(example_class)
    class Ex2(example_class):  # type: ignore[misc]
        @docfiller_float(example_class.meth)
        def meth(self) -> None:
            pass

        @docfiller_float(example_class.meth2)
        def meth2(self) -> None:
            pass

    compare_docs(
        Ex2.__doc__,
        expected_class.format(type_="float", summary="A class to do a thing"),
    )
    compare_docs(
        Ex2.meth.__doc__, expected_meth.format(type_="float", summary="A meth")
    )
    compare_docs(
        Ex2.meth2.__doc__, expected_meth.format(type_="float", summary="A meth2")
    )


def test_inherit_3(
    example_class: Any,
    docfiller_float: DocFiller,
    expected_class: str,
    expected_meth: str,
) -> None:
    expected_meth4 = expected_meth + dedent(
        """
    Notes
    -----
    {notes}
    """
    )

    for d in [
        docinherit.factory_docfiller_from_parent(example_class, docfiller_float),
        docfiller_float.factory_from_parent(example_class),
    ]:

        @d(example_class)
        class Ex3(example_class):  # type: ignore[misc]
            @d()
            def meth(self) -> None:
                pass

            @d()
            def meth2(self) -> None:
                pass

            # specify method name
            @d("meth")
            def meth3(self) -> None:
                pass

            @d("meth", notes="Hello there")
            def meth4(self) -> None:
                """
                Notes
                -----
                {notes}
                """

        compare_docs(
            Ex3.__doc__,
            expected_class.format(type_="float", summary="A class to do a thing"),
        )
        compare_docs(
            Ex3.meth.__doc__, expected_meth.format(type_="float", summary="A meth")
        )
        compare_docs(
            Ex3.meth2.__doc__, expected_meth.format(type_="float", summary="A meth2")
        )
        compare_docs(Ex3.meth.__doc__, Ex3.meth3.__doc__)
        compare_docs(
            Ex3.meth4.__doc__,
            expected_meth4.format(type_="float", summary="A meth", notes="Hello there"),
        )


def test_inherit_4(example_class: Any) -> None:
    d = docinherit.factory_docinherit_from_parent(example_class)

    @d(example_class)
    class Ex4(example_class):  # type: ignore[misc]
        """
        A new class

        Parameters
        ----------
        x : str
            x parameter.

        Notes
        -----
        Stuff
        """

        @d()
        def meth(self, z: str) -> str:
            """
            Parameters
            ----------
            z : str
                other parameter.

            Notes
            -----
            A note
            """
            return z

        @d()
        def meth2(self, z: str) -> str:
            """
            Parameters
            ----------
            z : str
                other parameter.

            Notes
            -----
            A note
            """
            return z

    expected_class4 = """
    {summary}

    Parameters
    ----------
    x : {type_}
        x parameter.
    y : int
        y parameter.

    Notes
    -----
    Stuff
    """

    expected_meth4 = """
    {summary}

    Parameters
    ----------
    z : {type_}
        other parameter.

    Notes
    -----
    A note
    """

    compare_docs(
        Ex4.__doc__, expected_class4.format(type_="str", summary="A new class")
    )
    compare_docs(Ex4.meth.__doc__, expected_meth4.format(type_="str", summary="A meth"))
    compare_docs(
        Ex4.meth2.__doc__, expected_meth4.format(type_="str", summary="A meth2")
    )


def test_inherit_5(example_class: Any, docfiller_str: DocFiller) -> None:
    expected_class5 = """
    {summary}

    Parameters
    ----------
    x : {type_}
        x parameter.
    y : {type_}
        y parameter.

    Notes
    -----
    {notes}
    """

    expected_meth5 = """
    {summary}

    Parameters
    ----------
    z : {type_}
        z parameter.

    Returns
    -------
    {output} : str
        {return_}

    Notes
    -----
    {notes}
    """

    for d in [
        docinherit.factory_docfiller_inherit_from_parent(
            example_class, docfiller=docfiller_str
        ),
        docfiller_str.factory_inherit_from_parent(example_class),
    ]:

        @d(example_class)
        class Ex5(example_class):  # type: ignore[misc]
            """
            A new class

            Notes
            -----
            class notes
            """

            @d()
            def meth(self, z: str) -> str:
                """
                Parameters
                ----------
                {z}

                Returns
                -------
                output : str
                    return

                Notes
                -----
                Meth notes
                """
                return z

            @d()
            def meth2(self, z: str) -> str:
                """
                Returns
                -------
                output2 : str
                    return2

                Notes
                -----
                Meth2 notes
                """
                return z

            @d("meth")
            def meth3(self, z: str) -> str:
                """
                Parameters
                ----------
                {z}

                Returns
                -------
                output : str
                    return

                Notes
                -----
                Meth notes
                """
                return z

            @d(example_class.meth, notes="Meth notes")
            def meth4(self, z: str) -> str:
                """
                Parameters
                ----------
                {z}

                Returns
                -------
                output : str
                    return

                Notes
                -----
                Meth notes
                """
                return z

        compare_docs(
            Ex5.__doc__,
            expected_class5.format(
                type_="str", summary="A new class", notes="class notes"
            ),
        )
        compare_docs(
            Ex5.meth.__doc__,
            expected_meth5.format(
                type_="str",
                summary="A meth",
                notes="Meth notes",
                output="output",
                return_="return",
            ),
        )
        compare_docs(
            Ex5.meth2.__doc__,
            expected_meth5.format(
                type_="str",
                summary="A meth2",
                notes="Meth2 notes",
                output="output2",
                return_="return2",
            ),
        )
        compare_docs(Ex5.meth3.__doc__, Ex5.meth.__doc__)
        compare_docs(Ex5.meth4.__doc__, Ex5.meth.__doc__)
