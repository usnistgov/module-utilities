from textwrap import dedent
from typing_extensions import reveal_type
from module_utilities.docfiller import DocFiller

import pytest


@pytest.fixture
def docstring_template():
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


@pytest.fixture
def docfiller1(docstring_template) -> DocFiller:
    return DocFiller.from_docstring(
        docstring_template.format(type_="int"), combine_keys="parameters"
    ).assign(klass="int")


@pytest.fixture
def docfiller2(docstring_template) -> DocFiller:
    return DocFiller.from_docstring(
        docstring_template.format(type_="float"), combine_keys="parameters"
    ).assign(klass="float")


def test_calibrate(docfiller1: DocFiller, docfiller2: DocFiller) -> None:
    expected_template = """
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

    expected_template = dedent(expected_template)

    @docfiller1.decorate
    def test1(x: int, y: int) -> int:
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

    reveal_type(test1)
    reveal_type(test1(1, 2))

    assert test1.__doc__ == expected_template.format(summary="Test1", type_="int")

    @docfiller2(test1)
    def test2(x: float, y: float) -> float:
        return x + y

    reveal_type(test2)
    reveal_type(test2(1.0, 2.0))

    assert test2.__doc__ == expected_template.format(summary="Test1", type_="float")

    # using inherit
    @docfiller2.inherit(test1)
    def test3(x: float, y: float) -> float:
        return x + y

    # note that doc inherit strips leading/trailing newlines.
    assert test3.__doc__.strip() == expected_template.format(summary="Test1", type_="float").strip()  # type: ignore

    reveal_type(test3)
    reveal_type(test3(1.0, 2.0))

    # test inherit
    expected_template = """
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

    expected_template = dedent(expected_template)

    # Note: theres a bug with custom_inhert.  Need the extra space to make indentation work
    @docfiller2.inherit(test1)
    def test4(x: float, y: float, z: int) -> float:
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

    reveal_type(test4)

    assert test4.__doc__.strip() == expected_template.format(summary="Testz", type_="float").strip()  # type: ignore

    @docfiller2.assign(type_="float").assign_param(
        "z", "float", "z parameter."
    ).inherit(test1)
    def test5(x: float, y: float, z: int) -> float:
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

    assert test5.__doc__.strip() == expected_template.format(summary="Testz", type_="float").strip()  # type: ignore


# def test_class_inherit(docfiller1: DocFiller, docfiller2: DocFiller) -> None:
