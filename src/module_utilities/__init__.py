"""
Top level API :mod:`module_utilities`
=====================================
"""
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

try:
    __version__ = _version("module-utilities")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "999"

__author__ = """William P. Krekelberg"""
__email__ = "wpk@nist.gov"

from . import cached, docfiller

__all__ = [
    "cached",
    "docfiller",
    "__version__",
]
