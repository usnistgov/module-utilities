#!/usr/bin/env python

"""Tests for `module_utilities` package."""

import pytest


from module_utilities import a_function, another_func


@pytest.fixture
def response():
    return 1, 2


def test_a_function(response):
    a, b = response
    assert a_function(a, b) == (a, b)


def test_another_function(response):
    a, b = response
    assert another_func(a, b) == a + b
