"""
Top level API :mod:`module_utilities`
=====================================
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from . import cached, docfiller

try:  # noqa: RUF067
    __version__ = _version("module-utilities")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "999"


__author__ = """William P. Krekelberg"""
__email__ = "wpk@nist.gov"  # noqa: RUF067

__all__ = [
    "__version__",
    "cached",
    "docfiller",
]
