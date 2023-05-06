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

from idom_router.types import Route, RouteCompiler, RouteResolver, Router

R = TypeVar("R", bound=Route)


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
    router_state = use_context(_route_state_context)


    if router_state is not None:
        raise RuntimeError("Another router is already active in this context")

    # Memoize the compiled routes and the match separately so that we don't
    # recompile the routes on renders where only the location has changed
    compiled_routes = use_memo(lambda: _compile_routes(routes, compiler))
    match = use_memo(lambda: _match_route(compiled_routes, location))

    if match is not None:
        route, params = match
        return ConnectionContext(
            _route_state_context(
                route.element, value=_RouteState(set_location, params)
            ),
            value=Connection(old_conn.scope, location, old_conn.carrier),
            key=route.path,
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


def _compile_routes(
    routes: Sequence[R], compiler: RouteCompiler[R]
) -> list[tuple[Any, RouteResolver]]:
    return [(r, compiler(r)) for r in _iter_routes(routes)]


def _iter_routes(routes: Sequence[R]) -> Iterator[R]:
    for parent in routes:
        for child in _iter_routes(parent.routes):
            yield replace(child, path=parent.path + child.path)
        yield parent


def _match_route(
    compiled_routes: list[tuple[R, RouteResolver]], location: Location
) -> tuple[R, dict[str, Any]] | None:
    for route, pattern in compiled_routes:
        params = pattern.match(location.pathname)
        if params is not None:  # explicitely None check (could be empty dict)
            return route, params
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
