# the version is statically loaded by setup.py
__version__ = "0.0.1"

from .router import (
    Route,
    link,
    router,
    use_location,
    use_params,
    use_query,
)

__all__ = [
    "Route",
    "link",
    "router",
    "use_location",
    "use_params",
    "use_query",
]
