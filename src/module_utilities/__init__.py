"""
Top level API :mod:`module_utilities`
=====================================
"""


from . import cached, docfiller

# updated versioning scheme
try:
    from importlib.metadata import version as _version
except ImportError:
    # if the fallback library is missing, we are doomed.
    from importlib_metadata import version as _version  # type: ignore[no-redef]

try:
    __version__ = _version("module_utilities")
except Exception:
    # Local copy or not installed with setuptools.
    # Disable minimum version checks on downstream libraries.
    __version__ = "999"


__author__ = """William P. Krekelberg"""
__email__ = "wpk@nist.gov"


__all__ = [
    "cached",
    "docfiller",
    "__version__",
]
