# the version is statically loaded by setup.py
__version__ = "0.0.1"

from idom_router.types import Route, RouteCompiler, RoutePattern

from .router import link, router, use_params, use_query

__all__ = [
    "link",
    "Route",
    "RouteCompiler",
    "RoutePattern",
    "router",
    "use_location",
    "use_params",
    "use_query",
]
