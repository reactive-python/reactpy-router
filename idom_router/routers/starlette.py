from __future__ import annotations

import re
from typing import Any

from starlette.convertors import Convertor
from starlette.routing import compile_path

from idom_router.types import Route
from idom_router.core import create_router


def compile_starlette_route(route: Route) -> StarletteRouteResolver:
    pattern, _, converters = compile_path(route.path)
    return StarletteRouteResolver(pattern, converters)


class StarletteRouteResolver:
    def __init__(
        self,
        pattern: re.Pattern[str],
        converters: dict[str, Convertor],
    ) -> None:
        self.pattern = pattern
        self.key = pattern.pattern
        self.converters = converters

    def match(self, path: str) -> dict[str, Any] | None:
        match = self.pattern.match(path)
        if match:
            return {
                k: self.converters[k].convert(v) if k in self.converters else v
                for k, v in match.groupdict().items()
            }
        return None


starlette_router = create_router(compile_starlette_route)
