from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence, TypeVar

from idom.types import Key, ComponentType
from typing_extensions import Protocol, Self


@dataclass
class Route:
    path: str
    element: Any
    routes: Sequence[Self]

    def __init__(
        self,
        path: str,
        element: Any | None,
        *routes_: Self,
        # we need kwarg in order to play nice with the expected dataclass interface
        routes: Sequence[Self] = (),
    ) -> None:
        self.path = path
        self.element = element
        self.routes = (*routes_, *routes)


class Router(Protocol):
    def __call__(self, *routes: Route) -> ComponentType:
        """Return a component that renders the first matching route"""


R = TypeVar("R", bound=Route, contravariant=True)


class RouteCompiler(Protocol[R]):
    def __call__(self, route: R) -> RouteResolver:
        """Compile a route into a resolver that can be matched against a path"""


class RouteResolver(Protocol):
    """A compiled route that can be matched against a path"""

    @property
    def key(self) -> Key:
        """Uniquely identified this resolver"""

    def resolve(self, path: str) -> tuple[Any, dict[str, Any]] | None:
        """Return the path's associated element and path params or None"""
