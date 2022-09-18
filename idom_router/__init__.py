# the version is statically loaded by setup.py
__version__ = "0.0.1"

from .router import (
    Route,
    RoutesConstructor,
    configure,
    link,
    use_location,
    use_params,
    use_query,
)

__all__ = [
    "configure",
    "link",
    "Route",
    "RoutesConstructor",
    "use_location",
    "use_params",
    "use_query",
]
