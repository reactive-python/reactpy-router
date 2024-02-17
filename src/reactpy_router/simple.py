"""A simple router implementation for ReactPy"""

from __future__ import annotations

import re
import uuid
from typing import Any, Callable

from typing_extensions import TypeAlias, TypedDict

from reactpy_router.core import create_router
from reactpy_router.types import Route

__all__ = ["router"]

ConversionFunc: TypeAlias = "Callable[[str], Any]"
ConverterMapping: TypeAlias = "dict[str, ConversionFunc]"

STAR_PATTERN = re.compile("^.*$")
PARAM_PATTERN = re.compile(r"{(?P<name>\w+)(?P<type>:\w+)?}")


class SimpleResolver:
    """A simple route resolver that uses regex to match paths"""

    def __init__(self, route: Route) -> None:
        self.element = route.element
        self.pattern, self.converters = parse_path(route.path)
        self.key = self.pattern.pattern

    def resolve(self, path: str) -> tuple[Any, dict[str, Any]] | None:
        match = self.pattern.match(path)
        if match:
            return (
                self.element,
                {k: self.converters[k](v) for k, v in match.groupdict().items()},
            )
        return None


def parse_path(path: str) -> tuple[re.Pattern[str], ConverterMapping]:
    if path == "*":
        return STAR_PATTERN, {}

    pattern = "^"
    last_match_end = 0
    converters: ConverterMapping = {}
    for match in PARAM_PATTERN.finditer(path):
        param_name = match.group("name")
        param_type = (match.group("type") or "str").lstrip(":")
        try:
            param_conv = CONVERSION_TYPES[param_type]
        except KeyError:
            raise ValueError(f"Unknown conversion type {param_type!r} in {path!r}")
        pattern += re.escape(path[last_match_end : match.start()])
        pattern += f"(?P<{param_name}>{param_conv['regex']})"
        converters[param_name] = param_conv["func"]
        last_match_end = match.end()
    pattern += re.escape(path[last_match_end:]) + "$"
    return re.compile(pattern), converters


class ConversionInfo(TypedDict):
    """Information about a conversion type"""

    regex: str
    """The regex to match the conversion type"""
    func: ConversionFunc
    """The function to convert the matched string to the expected type"""


CONVERSION_TYPES: dict[str, ConversionInfo] = {
    "str": {
        "regex": r"[^/]+",
        "func": str,
    },
    "int": {
        "regex": r"\d+",
        "func": int,
    },
    "float": {
        "regex": r"\d+(\.\d+)?",
        "func": float,
    },
    "uuid": {
        "regex": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "func": uuid.UUID,
    },
    "path": {
        "regex": r".+",
        "func": str,
    },
}
"""The supported conversion types"""


router = create_router(SimpleResolver)
"""The simple router"""
