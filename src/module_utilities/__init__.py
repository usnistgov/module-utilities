"""
Top level API :mod:`module_utilities`
=====================================
"""


from . import cached, docfiller

try:
    from ._version import __version__
except Exception:
    __version__ = "999"


__author__ = """William P. Krekelberg"""
__email__ = "wpk@nist.gov"


__all__ = [
    "cached",
    "docfiller",
    "__version__",
]
