from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence, TypeVar

from idom.types import Key
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


R = TypeVar("R", bound=Route, contravariant=True)


class RouteCompiler(Protocol[R]):
    def __call__(self, route: R) -> RoutePattern:
        """Compile a route into a pattern that can be matched against a path"""


class RoutePattern(Protocol):
    @property
    def key(self) -> Key:
        """Uniquely identified this pattern"""

    def match(self, path: str) -> dict[str, Any] | None:
        """Returns otherwise a dict of path parameters if the path matches, else None"""
