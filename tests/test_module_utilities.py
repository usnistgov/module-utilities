# mypy: disable-error-code="no-untyped-def"
"""Tests for `module_utilities` package."""


<<<<<<< before updating
def test_import() -> None:
    import module_utilities

    assert hasattr(module_utilities, "__version__")
=======
import re

import pytest

from module_utilities import example_function


def test_version() -> None:
    from module_utilities import __version__

    assert isinstance(__version__, str)
    assert re.match(r"^\d+\.\d+\.\d+.*$", __version__) is not None


@pytest.fixture
def response() -> tuple[int, int]:
    return 1, 2


def test_example_function(response: tuple[int, int]) -> None:
    expected = 3
    assert example_function(*response) == expected
>>>>>>> after updating
