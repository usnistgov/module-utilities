"""Top level configuration"""

import pytest


@pytest.fixture(autouse=True)
def add_standard_imports(doctest_namespace):
    from module_utilities import cached

    doctest_namespace["cached"] = cached
