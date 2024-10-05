# the version is statically loaded by setup.py
__version__ = "0.1.1"


from .converters import CONVERTERS
from .core import (
    create_router,
    link,
    route,
    router,
    use_params,
    use_search_params,
)
from .resolvers import Resolver
from .routers import browser_router
from .types import Route, RouteCompiler, RouteResolver

__all__ = (
    "create_router",
    "link",
    "route",
    "Route",
    "RouteCompiler",
    "router",
    "RouteResolver",
    "browser_router",
    "use_params",
    "use_search_params",
    "Resolver",
    "CONVERTERS",
)
