from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence
from urllib.parse import parse_qs

from idom import component, create_context, use_context, use_memo, use_state
from idom.core.types import VdomAttributesAndChildren, VdomDict
from idom.core.vdom import coalesce_attributes_and_children
from idom.types import BackendImplementation, ComponentType, Context, Location
from idom.web.module import export, module_from_file
from starlette.routing import compile_path

try:
    from typing import Protocol
except ImportError:  # pragma: no cover
    from typing_extensions import Protocol  # type: ignore


class RouterConstructor(Protocol):
    def __call__(self, *routes: Route) -> ComponentType:
        ...


def create_router(
    implementation: BackendImplementation[Any] | Callable[[], Location]
) -> RouterConstructor:
    if isinstance(implementation, BackendImplementation):
        use_location = implementation.use_location
    elif callable(implementation):
        use_location = implementation
    else:
        raise TypeError(
            "Expected a 'BackendImplementation' or "
            f"'use_location' hook, not {implementation}"
        )

    @component
    def router(*routes: Route) -> ComponentType | None:
        initial_location = use_location()
        location, set_location = use_state(initial_location)
        compiled_routes = use_memo(
            lambda: _iter_compile_routes(routes), dependencies=routes
        )
        for r in compiled_routes:
            match = r.pattern.match(location.pathname)
            if match:
                return _LocationStateContext(
                    r.element,
                    value=_LocationState(
                        location,
                        set_location,
                        {k: r.converters[k](v) for k, v in match.groupdict().items()},
                    ),
                    key=r.pattern.pattern,
                )
        return None

    return router


@dataclass
class Route:
    path: str
    element: Any
    routes: Sequence[Route]

    def __init__(self, path: str, element: Any | None, *routes: Route) -> None:
        self.path = path
        self.element = element
        self.routes = routes


@component
def link(*attributes_or_children: VdomAttributesAndChildren, to: str) -> VdomDict:
    attributes, children = coalesce_attributes_and_children(attributes_or_children)
    set_location = _use_location_state().set_location
    attrs = {
        **attributes,
        "to": to,
        "onClick": lambda event: set_location(Location(**event)),
    }
    return _Link(attrs, *children)


def use_location() -> Location:
    """Get the current route location"""
    return _use_location_state().location


def use_params() -> dict[str, Any]:
    """Get parameters from the currently matching route pattern"""
    return _use_location_state().params


def use_query(
    keep_blank_values: bool = False,
    strict_parsing: bool = False,
    errors: str = "replace",
    max_num_fields: int | None = None,
    separator: str = "&",
) -> dict[str, list[str]]:
    """See :func:`urllib.parse.parse_qs` for parameter info."""
    return parse_qs(
        use_location().search[1:],
        keep_blank_values=keep_blank_values,
        strict_parsing=strict_parsing,
        errors=errors,
        max_num_fields=max_num_fields,
        separator=separator,
    )


def _iter_compile_routes(routes: Sequence[Route]) -> Iterator[_CompiledRoute]:
    for path, element in _iter_routes(routes):
        pattern, _, converters = compile_path(path)
        yield _CompiledRoute(
            pattern, {k: v.convert for k, v in converters.items()}, element
        )


def _iter_routes(routes: Sequence[Route]) -> Iterator[tuple[str, Any]]:
    for r in routes:
        for path, element in _iter_routes(r.routes):
            yield r.path + path, element
        yield r.path, r.element


@dataclass
class _CompiledRoute:
    pattern: re.Pattern[str]
    converters: dict[str, Callable[[Any], Any]]
    element: Any


def _use_location_state() -> _LocationState:
    location_state = use_context(_LocationStateContext)
    assert location_state is not None, "No location state. Did you use a Router?"
    return location_state


@dataclass
class _LocationState:
    location: Location
    set_location: Callable[[Location], None]
    params: dict[str, Any]


_LocationStateContext: Context[_LocationState | None] = create_context(None)

_Link = export(
    module_from_file(
        "idom-router",
        file=Path(__file__).parent / "bundle.js",
        fallback="⏳",
    ),
    "Link",
)
