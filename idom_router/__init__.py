# the version is statically loaded by setup.py
__version__ = "0.0.1"

from idom_router.types import Route, RouteCompiler, RouteResolver

from .core import link, create_router, router_component, use_params, use_query

__all__ = [
    "create_router",
    "link",
    "Route",
    "RouteCompiler",
    "router_component",
    "RouteResolver",
    "use_location",
    "use_params",
    "use_query",
]
