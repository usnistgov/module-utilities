#!/usr/bin/env python

"""Tests for `module_utilities` package."""


def test_import():
    import module_utilities

    assert hasattr(module_utilities, "__version__")
