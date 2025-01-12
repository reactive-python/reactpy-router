"""URL router implementation for ReactPy"""

from __future__ import annotations

from dataclasses import replace
from logging import getLogger
from typing import TYPE_CHECKING, Any, Union, cast

from reactpy import component, use_memo, use_state
from reactpy.backend.types import Connection, Location
from reactpy.core.hooks import ConnectionContext, use_connection
from reactpy.types import ComponentType, VdomDict

from reactpy_router.components import History
from reactpy_router.hooks import RouteState, _route_state_context
from reactpy_router.resolvers import ReactPyResolver

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from reactpy.core.component import Component

    from reactpy_router.types import CompiledRoute, MatchedRoute, Resolver, Route, Router

__all__ = ["browser_router", "create_router"]
_logger = getLogger(__name__)


def create_router(resolver: Resolver[Route]) -> Router[Route]:
    """A decorator that turns a resolver into a router"""

    def wrapper(*routes: Route) -> Component:
        return router(*routes, resolver=resolver)

    return wrapper


_router = create_router(ReactPyResolver)


def browser_router(*routes: Route) -> Component:
    """This is the recommended router for all ReactPy-Router web projects.
    It uses the JavaScript [History API](https://developer.mozilla.org/en-US/docs/Web/API/History_API)
    to manage the history stack.

    Args:
        *routes (Route): A list of routes to be rendered by the router.

    Returns:
        A router component that renders the given routes.
    """
    return _router(*routes)


@component
def router(
    *routes: Route,
    resolver: Resolver[Route],
) -> VdomDict | None:
    """A component that renders matching route using the given resolver.

    User notice: This component typically should never be used. Instead, use `create_router` if creating
    a custom routing engine."""

    old_connection = use_connection()
    location, set_location = use_state(cast(Union[Location, None], None))
    resolvers = use_memo(
        lambda: tuple(map(resolver, _iter_routes(routes))),
        dependencies=(resolver, hash(routes)),
    )
    route_element = None
    match = use_memo(lambda: _match_route(resolvers, location or old_connection.location))

    if match:
        # Skip rendering until ReactPy-Router knows what URL the page is on.
        if location:
            route_element = _route_state_context(
                match.element,
                value=RouteState(set_location, match.params),
            )

        def on_history_change(event: dict[str, Any]) -> None:
            """Callback function used within the JavaScript `History` component."""
            new_location = Location(**event)
            if location != new_location:
                set_location(new_location)

        return ConnectionContext(
            History({"onHistoryChangeCallback": on_history_change}),  # type: ignore[return-value]
            route_element,
            value=Connection(old_connection.scope, location or old_connection.location, old_connection.carrier),
        )

    return None


def _iter_routes(routes: Sequence[Route]) -> Iterator[Route]:
    for parent in routes:
        for child in _iter_routes(parent.routes):
            yield replace(child, path=parent.path + child.path)  # type: ignore[misc]
        yield parent


def _add_route_key(match: MatchedRoute, key: str | int) -> Any:
    """Add a key to the VDOM or component on the current route, if it doesn't already have one."""
    element = match.element
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
) -> MatchedRoute | None:
    for resolver in compiled_routes:
        match = resolver.resolve(location.pathname)
        if match is not None:
            return _add_route_key(match, resolver.key)

    _logger.debug("No matching route found for %s", location.pathname)

    return None
