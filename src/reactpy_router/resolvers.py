from __future__ import annotations

import re
from typing import Any

from reactpy_router.converters import CONVERTERS
from reactpy_router.types import ConversionInfo, ConverterMapping, Route

__all__ = ["StarletteResolver"]


class StarletteResolver:
    """URL resolver that matches routes that match the starlette URL routing syntax.

    However, we add a few additional parameter types on top of Starlette's syntax."""

    def __init__(
        self,
        route: Route,
        param_pattern=r"{(?P<name>\w+)(?P<type>:\w+)?}",
        converters: dict[str, ConversionInfo] | None = None,
    ) -> None:
        self.element = route.element
        self.registered_converters = converters or CONVERTERS
        self.converter_mapping: ConverterMapping = {}
        self.param_regex = re.compile(param_pattern)
        self.pattern = self.parse_path(route.path)
        self.key = self.pattern.pattern  # Unique identifier for ReactPy rendering

    def parse_path(self, path: str) -> re.Pattern[str]:
        # Convert path to regex pattern, then interpret using registered converters
        pattern = "^"
        last_match_end = 0

        # Iterate through matches of the parameter pattern
        for match in self.param_regex.finditer(path):
            # Extract parameter name and type
            name = match.group("name")
            if name[0].isnumeric():
                name = f"_numeric_{name}"
            param_type = (match.group("type") or "str").strip(":")

            # Check if a converter exists for the type
            try:
                conversion_info = self.registered_converters[param_type]
            except KeyError as e:
                raise ValueError(f"Unknown conversion type {param_type!r} in {path!r}") from e

            # Add the string before the match to the pattern
            pattern += re.escape(path[last_match_end : match.start()])

            # Add the match to the pattern
            pattern += f"(?P<{name}>{conversion_info['regex']})"

            # Keep a local mapping of parameter names to conversion functions.
            self.converter_mapping[name] = conversion_info["func"]

            # Update the last match end
            last_match_end = match.end()

        # Add the string after the last match
        pattern += f"{re.escape(path[last_match_end:])}$"

        return re.compile(pattern)

    def resolve(self, path: str) -> tuple[Any, dict[str, Any]] | None:
        match = self.pattern.match(path)
        if match:
            # Convert the matched groups to the correct types
            params = {
                parameter_name[len("_numeric_") :]
                if parameter_name.startswith("_numeric_")
                else parameter_name: self.converter_mapping[parameter_name](value)
                for parameter_name, value in match.groupdict().items()
            }
            return (self.element, params)
        return None
