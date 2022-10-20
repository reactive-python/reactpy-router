from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Any, Protocol, Sequence


@dataclass
class Route:
    path: str
    element: Any
    routes: Sequence[Route]

    def __init__(self, path: str, element: Any | None, *routes: Route) -> None:
        self.path = path
        self.element = element
        self.routes = routes


class RouteCompiler(Protocol):
    def __call__(self, route: str) -> RoutePattern:
        ...


@dataclass
class RoutePattern:
    pattern: re.Pattern[str]
    converters: dict[str, Callable[[Any], Any]]
