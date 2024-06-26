import re
from typing import Any

from reactpy_router.converters import CONVERTERS
from reactpy_router.types import ConversionInfo, ConverterMapping, Route

__all__ = ["Resolver"]


class Resolver:
    """A simple route resolver that uses regex to match paths."""

    def __init__(
        self,
        route: Route,
        param_pattern=r"{(?P<name>\w+)(?P<type>:\w+)?}",
        match_any_identifier=r"\*$",
        converters: dict[str, ConversionInfo] | None = None,
    ) -> None:
        self.element = route.element
        self.pattern, self.converter_mapping = self.parse_path(route.path)
        self.registered_converters = converters or CONVERTERS
        self.key = self.pattern.pattern
        self.param_regex = re.compile(param_pattern)
        self.match_any = match_any_identifier

    def parse_path(self, path: str) -> tuple[re.Pattern[str], ConverterMapping]:
        # Convert path to regex pattern, then interpret using registered converters
        pattern = "^"
        last_match_end = 0
        converter_mapping: ConverterMapping = {}
        for match in self.param_regex.finditer(path):
            param_name = match.group("name")
            param_type = (match.group("type") or "str").strip(":")
            try:
                param_conv = self.registered_converters[param_type]
            except KeyError as e:
                raise ValueError(
                    f"Unknown conversion type {param_type!r} in {path!r}"
                ) from e
            pattern += re.escape(path[last_match_end : match.start()])
            pattern += f"(?P<{param_name}>{param_conv['regex']})"
            converter_mapping[param_name] = param_conv["func"]
            last_match_end = match.end()
        pattern += f"{re.escape(path[last_match_end:])}$"

        # Replace "match anything" pattern with regex, if it's at the end of the path
        if pattern.endswith(self.match_any):
            pattern = f"{pattern[:-3]}.*$"

        return re.compile(pattern), converter_mapping

    def resolve(self, path: str) -> tuple[Any, dict[str, Any]] | None:
        match = self.pattern.match(path)
        if match:
            return (
                self.element,
                {k: self.converter_mapping[k](v) for k, v in match.groupdict().items()},
            )
        return None
