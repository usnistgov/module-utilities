# mypy: disable-error-code="no-untyped-def"
"""Tests for `module_utilities` package."""


def test_import() -> None:
    import module_utilities

    assert hasattr(module_utilities, "__version__")
