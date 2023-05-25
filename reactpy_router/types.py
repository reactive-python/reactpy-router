"""Types for reactpy_router"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence, TypeVar

from reactpy.core.vdom import is_vdom
from reactpy.types import ComponentType, Key
from typing_extensions import Protocol, Self


@dataclass(frozen=True)
class Route:
    """A route that can be matched against a path"""

    path: str
    """The path to match against"""

    element: Any = field(hash=False)
    """The element to render if the path matches"""

    routes: Sequence[Self]
    """Child routes"""

    def __hash__(self) -> int:
        el = self.element
        key = el["key"] if is_vdom(el) and "key" in el else getattr(el, "key", id(el))
        return hash((self.path, key, self.routes))


R = TypeVar("R", bound=Route, contravariant=True)


class Router(Protocol[R]):
    """Return a component that renders the first matching route"""

    def __call__(self, *routes: R) -> ComponentType:
        ...


class RouteCompiler(Protocol[R]):
    """Compile a route into a resolver that can be matched against a path"""

    def __call__(self, route: R) -> RouteResolver:
        ...


class RouteResolver(Protocol):
    """A compiled route that can be matched against a path"""

    @property
    def key(self) -> Key:
        """Uniquely identified this resolver"""

    def resolve(self, path: str) -> tuple[Any, dict[str, Any]] | None:
        """Return the path's associated element and path params or None"""
