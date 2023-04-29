from __future__ import annotations

import re
from typing import Any, Callable

from idom_router import Route


def compile_simple_regex_route(route: Route) -> RegexRoutePattern:
    """Compile simple regex route.

    Named regex groups can end with a `__type` suffix to specify a type converter

    For example, `(?P<id__int>[0-9]+)` will convert the `id` parameter to an `int`.

    Supported types are `int`, `float`, and `list` where `list` will split on `,`.
    """
    pattern = re.compile(route.path)
    return RegexRoutePattern(pattern)


class RegexRoutePattern:
    def __init__(self, pattern: re.Pattern) -> None:
        self.pattern = pattern
        self.key = pattern.pattern

    def match(self, path: str) -> dict[str, str] | None:
        match = self.pattern.match(path)
        if match:
            params: dict[str, Any] = {}
            for k, v in match.groupdict().items():
                name, _, type_ = k.partition("__")
                try:
                    params[name] = CONVERTERS.get(type_, DEFAULT_CONVERTER)(v)
                except ValueError:
                    return None
            return params
        return None


CONVERTERS: dict[str, Callable[[str], Any]] = {
    "int": int,
    "float": float,
    "list": lambda s: s.split(","),
}


def DEFAULT_CONVERTER(s: str) -> str:
    return s
