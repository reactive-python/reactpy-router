"""URL router implementation for ReactPy"""

from __future__ import annotations

from dataclasses import replace
from logging import getLogger
from typing import Any, Iterator, Literal, Sequence, cast

from reactpy import component, use_memo, use_state
from reactpy.backend.hooks import ConnectionContext, use_connection
from reactpy.backend.types import Connection, Location
from reactpy.types import ComponentType, VdomDict

from reactpy_router.components import History
from reactpy_router.hooks import _route_state_context, _RouteState
from reactpy_router.resolvers import StarletteResolver
from reactpy_router.types import CompiledRoute, Resolver, Router, RouteType

__all__ = ["browser_router", "create_router"]
_logger = getLogger(__name__)


def create_router(resolver: Resolver[RouteType]) -> Router[RouteType]:
    """A decorator that turns a resolver into a router"""

    def wrapper(*routes: RouteType) -> ComponentType:
        return router(*routes, resolver=resolver)

    return wrapper


browser_router = create_router(StarletteResolver)
"""This is the recommended router for all ReactPy Router web projects.
It uses the JavaScript DOM History API to manage the history stack."""


@component
def router(
    *routes: RouteType,
    resolver: Resolver[RouteType],
) -> VdomDict | None:
    """A component that renders matching route(s) using the given resolver.

    This typically should never be used by a user. Instead, use `create_router` if creating
    a custom routing engine."""

    old_conn = use_connection()
    location, set_location = use_state(old_conn.location)

    resolvers = use_memo(
        lambda: tuple(map(resolver, _iter_routes(routes))),
        dependencies=(resolver, hash(routes)),
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

        def on_history_change(event: dict[str, Any]) -> None:
            """Callback function used within the JavaScript `History` component."""
            new_location = Location(**event)
            if location != new_location:
                set_location(new_location)

        return ConnectionContext(
            History({"onHistoryChangeCallback": on_history_change}),  # type: ignore[return-value]
            *route_elements,
            value=Connection(old_conn.scope, location, old_conn.carrier),
        )

    return None


def _iter_routes(routes: Sequence[RouteType]) -> Iterator[RouteType]:
    for parent in routes:
        for child in _iter_routes(parent.routes):
            yield replace(child, path=parent.path + child.path)  # type: ignore[misc]
        yield parent


def _add_route_key(match: tuple[Any, dict[str, Any]], key: str | int) -> Any:
    """Add a key to the VDOM or component on the current route, if it doesn't already have one."""
    element, _params = match
    if hasattr(element, "render") and not element.key:
        element = cast(ComponentType, element)
        element.key = key
    elif isinstance(element, dict) and not element.get("key", None):
        element = cast(VdomDict, element)
        element["key"] = key
    return match


def _match_route(
    compiled_routes: Sequence[CompiledRoute],
    location: Location,
    select: Literal["first", "all"],
) -> list[tuple[Any, dict[str, Any]]]:
    matches = []

    for resolver in compiled_routes:
        match = resolver.resolve(location.pathname)
        if match is not None:
            if select == "first":
                return [_add_route_key(match, resolver.key)]

            # Matching multiple routes is disabled since `react-router` no longer supports multiple
            # matches via the `Route` component. However, it's kept here to support future changes
            # or third-party routers.
            # TODO: The `resolver.key` value has edge cases where it is not unique enough to use as
            # a key here, unless we begin throwing errors for duplicate routes.
            matches.append(_add_route_key(match, resolver.key))  # pragma: no cover

    if not matches:
        _logger.debug("No matching route found for %s", location.pathname)

    return matches
