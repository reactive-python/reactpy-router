from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence, TypeVar
from urllib.parse import parse_qs

from idom import (
    component,
    create_context,
    use_context,
    use_location,
    use_memo,
    use_state,
)
from idom.backend.hooks import ConnectionContext, use_connection
from idom.backend.types import Connection, Location
from idom.core.types import VdomChild, VdomDict
from idom.types import ComponentType, Context, Location
from idom.web.module import export, module_from_file

from idom_router.types import Route, RouteCompiler, Router, RouteResolver

R = TypeVar("R", bound=Route)


def route(path: str, element: Any | None, *routes: Route) -> Route:
    return Route(path, element, routes)


def create_router(compiler: RouteCompiler[R]) -> Router[R]:
    """A decorator that turns a route compiler into a router"""

    def wrapper(*routes: R) -> ComponentType:
        return router_component(*routes, compiler=compiler)

    return wrapper


@component
def router_component(
    *routes: R,
    compiler: RouteCompiler[R],
) -> ComponentType | None:
    old_conn = use_connection()
    location, set_location = use_state(old_conn.location)

    resolvers = use_memo(
        lambda: tuple(map(compiler, _iter_routes(routes))),
        dependencies=(compiler, hash(routes)),
    )

    match = use_memo(lambda: _match_route(resolvers, location))

    if match is not None:
        element, params = match
        return ConnectionContext(
            _route_state_context(element, value=_RouteState(set_location, params)),
            value=Connection(old_conn.scope, location, old_conn.carrier),
        )

    return None


@component
def link(*children: VdomChild, to: str, **attributes: Any) -> VdomDict:
    set_location = _use_route_state().set_location
    attrs = {
        **attributes,
        "to": to,
        "onClick": lambda event: set_location(Location(**event)),
    }
    return _link(attrs, *children)


def use_params() -> dict[str, Any]:
    """Get parameters from the currently matching route pattern"""
    return _use_route_state().params


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


def _iter_routes(routes: Sequence[R]) -> Iterator[R]:
    for parent in routes:
        for child in _iter_routes(parent.routes):
            yield replace(child, path=parent.path + child.path)  # type: ignore[misc]
        yield parent


def _match_route(
    compiled_routes: Sequence[RouteResolver], location: Location
) -> tuple[Any, dict[str, Any]] | None:
    for resolver in compiled_routes:
        match = resolver.resolve(location.pathname)
        if match is not None:
            return match
    return None


_link = export(
    module_from_file("idom-router", file=Path(__file__).parent / "bundle.js"),
    "Link",
)


@dataclass
class _RouteState:
    set_location: Callable[[Location], None]
    params: dict[str, Any]


def _use_route_state() -> _RouteState:
    route_state = use_context(_route_state_context)
    assert route_state is not None
    return route_state


_route_state_context: Context[_RouteState | None] = create_context(None)
