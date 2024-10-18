# the version is statically loaded by setup.py
__version__ = "1.0.0"


from .components import link, navigate, route
from .hooks import use_params, use_search_params
from .routers import browser_router, create_router

__all__ = (
    "create_router",
    "link",
    "route",
    "browser_router",
    "use_params",
    "use_search_params",
    "navigate",
)
