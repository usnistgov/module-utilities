"""Top level configuration"""

from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture(autouse=True)
def add_standard_imports(doctest_namespace: dict[str, Any]) -> None:
    from module_utilities import cached

    doctest_namespace["cached"] = cached
