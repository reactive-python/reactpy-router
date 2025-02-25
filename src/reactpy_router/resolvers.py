from __future__ import annotations

import re
from typing import TYPE_CHECKING, ClassVar

from reactpy_router.converters import CONVERTERS
from reactpy_router.types import MatchedRoute

if TYPE_CHECKING:
    from reactpy_router.types import ConversionInfo, ConverterMapping, Route

__all__ = ["ReactPyResolver"]


class ReactPyResolver:
    """URL resolver that can match a path against any given routes.

    URL routing syntax for this resolver is based on Starlette, and supports a mixture of Starlette and Django parameter types."""

    param_pattern: str = r"{(?P<name>\w+)(?P<type>:\w+)?}"
    converters: ClassVar[dict[str, ConversionInfo]] = CONVERTERS

    def __init__(self, route: Route) -> None:
        self.element = route.element
        self.converter_mapping: ConverterMapping = {}
        self.param_regex = re.compile(self.param_pattern)
        self.pattern = self.parse_path(route.path)
        self.key = self.pattern.pattern  # Unique identifier for ReactPy rendering

    def parse_path(self, path: str) -> re.Pattern[str]:
        # Convert path to regex pattern, then interpret using registered converters
        pattern = "^"
        last_match_end = 0

        # Iterate through matches of the parameter pattern
        for match in self.param_regex.finditer(path):
            # Extract parameter name
            name = match.group("name")
            if name[0].isnumeric():
                # Regex group names can't begin with a number, so we must prefix them with
                # "_numeric_". This prefix is removed later within this function.
                name = f"_numeric_{name}"

            # Extract the parameter type
            param_type = (match.group("type") or "str").strip(":")

            # Check if a converter exists for the type
            try:
                conversion_info = self.converters[param_type]
            except KeyError as e:
                msg = f"Unknown conversion type {param_type!r} in {path!r}"
                raise ValueError(msg) from e

            # Add the string before the match to the pattern
            pattern += re.escape(path[last_match_end : match.start()])

            # Add the match to the pattern
            pattern += f"(?P<{name}>{conversion_info['regex']})"

            # Keep a local mapping of the URL's parameter names to conversion functions.
            self.converter_mapping[name] = conversion_info["func"]

            # Update the last match end
            last_match_end = match.end()

        # Add the string after the last match
        pattern += f"{re.escape(path[last_match_end:])}$"

        return re.compile(pattern)

    def resolve(self, path: str) -> MatchedRoute | None:
        match = self.pattern.match(path)
        if match:
            # Convert the matched groups to the correct types
            params = {
                parameter_name[len("_numeric_") :]
                if parameter_name.startswith("_numeric_")
                else parameter_name: self.converter_mapping[parameter_name](value)
                for parameter_name, value in match.groupdict().items()
            }
            return MatchedRoute(self.element, params, path)
        return None
