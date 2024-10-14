import uuid

from reactpy_router.types import ConversionInfo

__all__ = ["CONVERTERS"]

CONVERTERS: dict[str, ConversionInfo] = {
    "int": {
        "regex": r"\d+",
        "func": int,
    },
    "str": {
        "regex": r"[^/]+",
        "func": str,
    },
    "uuid": {
        "regex": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "func": uuid.UUID,
    },
    "slug": {
        "regex": r"[-a-zA-Z0-9_]+",
        "func": str,
    },
    "path": {
        "regex": r".+",
        "func": str,
    },
    "float": {
        "regex": r"\d+(\.\d+)?",
        "func": float,
    },
    "any": {
        "regex": r".*",
        "func": str,
    },
}
"""The conversion types supported by the default Resolver."""
