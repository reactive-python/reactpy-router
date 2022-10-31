from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence
from urllib.parse import parse_qs

from idom import (
    component,
    create_context,
    use_memo,
    use_state,
    use_context,
    use_location,
)
from idom.core.types import VdomAttributesAndChildren, VdomDict
from idom.core.vdom import coalesce_attributes_and_children
from idom.types import ComponentType, Location, Context
from idom.web.module import export, module_from_file
from idom.backend.hooks import ConnectionContext, use_connection
from idom.backend.types import Connection, Location
from starlette.routing import compile_path as _compile_starlette_path

from idom_router.types import RoutePattern, RouteCompiler, Route


def compile_starlette_route(route: str) -> RoutePattern:
    pattern, _, converters = _compile_starlette_path(route)
    return RoutePattern(pattern, {k: v.convert for k, v in converters.items()})


@component
def router(
    *routes: Route,
    compiler: RouteCompiler = compile_starlette_route,
) -> ComponentType | None:
    old_conn = use_connection()
    location, set_location = use_state(old_conn.location)

    compiled_routes = use_memo(
        lambda: [(compiler(r), e) for r, e in _iter_routes(routes)],
        dependencies=routes,
    )
    for compiled_route, element in compiled_routes:
        match = compiled_route.pattern.match(location.pathname)
        if match:
            convs = compiled_route.converters
            return ConnectionContext(
                _route_state_context(
                    element,
                    value=_RouteState(
                        set_location,
                        {
                            k: convs[k](v) if k in convs else v
                            for k, v in match.groupdict().items()
                        },
                    ),
                ),
                value=Connection(old_conn.scope, location, old_conn.carrier),
                key=compiled_route.pattern.pattern,
            )
    return None


@component
def link(*attributes_or_children: VdomAttributesAndChildren, to: str) -> VdomDict:
    attributes, children = coalesce_attributes_and_children(attributes_or_children)
    set_location = _use_route_state().set_location
    attrs = {
        **attributes,
        "to": to,
        "onClick": lambda event: set_location(Location(**event)),
    }
    return _link(attrs, *children)


def use_params() -> dict[str, Any]:
    """Get parameters from the currently matching route pattern"""
    return use_context(_route_state_context).params


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


def _use_route_state() -> _RouteState:
    return use_context(_route_state_context)


def _iter_routes(routes: Sequence[Route]) -> Iterator[tuple[str, Any]]:
    for r in routes:
        for path, element in _iter_routes(r.routes):
            yield r.path + path, element
        yield r.path, r.element


_link = export(
    module_from_file("idom-router", file=Path(__file__).parent / "bundle.js"),
    "Link",
)


@dataclass
class _RouteState:
    set_location: Callable[[Location], None]
    params: dict[str, Any]


_route_state_context: Context[_RouteState | None] = create_context(None)
