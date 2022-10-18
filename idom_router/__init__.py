# the version is statically loaded by setup.py
__version__ = "0.0.1"

from .router import (
    Route,
    RouterConstructor,
    create_router,
    link,
    use_location,
    use_params,
    use_query,
)

__all__ = [
    "create_router",
    "link",
    "Route",
    "RouterConstructor",
    "use_location",
    "use_params",
    "use_query",
]
