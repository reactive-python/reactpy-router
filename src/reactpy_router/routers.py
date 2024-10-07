"""URL router implementation for ReactPy"""

from __future__ import annotations

from dataclasses import replace
from logging import getLogger
from typing import Any, Iterator, Literal, Sequence, TypeVar

from reactpy import (
    component,
    html,
    use_memo,
    use_state,
)
from reactpy.backend.hooks import ConnectionContext, use_connection
from reactpy.backend.types import Connection, Location
from reactpy.core.types import VdomDict
from reactpy.types import ComponentType

from reactpy_router.components import History
from reactpy_router.hooks import _route_state_context, _RouteState
from reactpy_router.resolvers import StarletteResolver
from reactpy_router.types import Route, RouteCompiler, Router, RouteResolver

__all__ = ["browser_router", "create_router"]
_logger = getLogger(__name__)
R = TypeVar("R", bound=Route)


def create_router(compiler: RouteCompiler[R]) -> Router[R]:
    """A decorator that turns a route compiler into a router"""

    def wrapper(*routes: R) -> ComponentType:
        return router(*routes, compiler=compiler)

    return wrapper


browser_router = create_router(StarletteResolver)
"""This is the recommended router for all ReactPy Router web projects.
It uses the DOM History API to update the URL and manage the history stack."""


@component
def router(
    *routes: R,
    compiler: RouteCompiler[R],
) -> VdomDict | None:
    """A component that renders matching route(s) using the given compiler function.

    This typically should never be used by a user. Instead, use `create_router` if creating
    a custom routing engine."""

    old_conn = use_connection()
    location, set_location = use_state(old_conn.location)

    resolvers = use_memo(
        lambda: tuple(map(compiler, _iter_routes(routes))),
        dependencies=(compiler, hash(routes)),
    )

    match = use_memo(lambda: _match_route(resolvers, location, select="first"))

    if match:
        route_elements = [
            _route_state_context(
                element,
                value=_RouteState(set_location, params),
            )
            for element, params in match
        ]
        return ConnectionContext(
            History(  # type: ignore
                {"on_change": lambda event: set_location(Location(**event))}
            ),
            html._(route_elements),
            value=Connection(old_conn.scope, location, old_conn.carrier),
        )

    return None


def _iter_routes(routes: Sequence[R]) -> Iterator[R]:
    for parent in routes:
        for child in _iter_routes(parent.routes):
            yield replace(child, path=parent.path + child.path)  # type: ignore[misc]
        yield parent


def _match_route(
    compiled_routes: Sequence[RouteResolver],
    location: Location,
    select: Literal["first", "all"],
) -> list[tuple[Any, dict[str, Any]]]:
    matches = []

    for resolver in compiled_routes:
        match = resolver.resolve(location.pathname)
        if match is not None:
            if select == "first":
                return [match]

            # This is no longer used by `reactpy-router`, since `react-router>=6.0.0` no longer supports
            # multiple matches. However, it's kept here to support future changes.
            matches.append(match)  # pragma: no cover

    if not matches:
        _logger.debug("No matching route found for %s", location.pathname)

    return matches
