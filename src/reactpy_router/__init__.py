# the version is statically loaded by setup.py
__version__ = "0.1.1"

from . import routers
from .core import create_router, link, route, router_component, use_params, use_search_params
from .routers import browser_router
from .types import Route, RouteCompiler, RouteResolver

__all__ = (
    "create_router",
    "link",
    "route",
    "route",
    "Route",
    "routers",
    "RouteCompiler",
    "router_component",
    "RouteResolver",
    "browser_router",
    "use_params",
    "use_search_params",
)
