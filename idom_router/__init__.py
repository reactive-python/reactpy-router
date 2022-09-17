# the version is statically loaded by setup.py
__version__ = "0.0.1"

from .router import Link, Route, Routes, configure, use_location

__all__ = [
    "configure",
    "Link",
    "Route",
    "Routes",
    "use_location",
]
