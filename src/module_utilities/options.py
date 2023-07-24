"""
Define optional parameters
==========================
"""

import os


def _get_doc_sub() -> bool:
    try:
        # Default is doc_sub is True
        return os.getenv("DOCFILLER_SUB", "True").lower() not in (
            "0",
            "f",
            "false",
        )
    except KeyError:
        return True


DOC_SUB = _get_doc_sub()
