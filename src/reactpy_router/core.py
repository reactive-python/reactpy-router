"""Core functionality for the reactpy-router package."""

from __future__ import annotations

from dataclasses import dataclass, replace
from logging import getLogger
from pathlib import Path
from typing import Any, Callable, Iterator, Literal, Sequence, TypeVar
from urllib.parse import parse_qs
from uuid import uuid4

from reactpy import (
    component,
    create_context,
    html,
    use_context,
    use_location,
    use_memo,
    use_state,
)
from reactpy.backend.hooks import ConnectionContext, use_connection
from reactpy.backend.types import Connection, Location
from reactpy.core.types import VdomChild, VdomDict
from reactpy.types import ComponentType, Context
from reactpy.web.module import export, module_from_file

from reactpy_router.types import Route, RouteCompiler, Router, RouteResolver

_logger = getLogger(__name__)
R = TypeVar("R", bound=Route)


def route(path: str, element: Any | None, *routes: Route) -> Route:
    """Create a route with the given path, element, and child routes"""
    return Route(path, element, routes)


def create_router(compiler: RouteCompiler[R]) -> Router[R]:
    """A decorator that turns a route compiler into a router"""

    def wrapper(*routes: R, select: Literal["first", "all"] = "first") -> ComponentType:
        return router_component(*routes, select=select, compiler=compiler)

    return wrapper


@component
def router_component(
    *routes: R,
    select: Literal["first", "all"],
    compiler: RouteCompiler[R],
) -> VdomDict | None:
    """A component that renders matching route(s) using the given compiler function."""

    old_conn = use_connection()
    location, set_location = use_state(old_conn.location)

    resolvers = use_memo(
        lambda: tuple(map(compiler, _iter_routes(routes))),
        dependencies=(compiler, hash(routes)),
    )

    match = use_memo(lambda: _match_route(resolvers, location, select))

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


@component
def link(*children: VdomChild, to: str, **attributes: Any) -> VdomDict:
    """A component that renders a link to the given path.

    FIXME: This currently works in a "dumb" way by trusting that ReactPy's script tag
    properly sets the location. When a client-server communication layer is added to
    ReactPy, this component will need to be rewritten to use that instead."""
    set_location = _use_route_state().set_location
    uuid = uuid4().hex

    def on_click(_event: dict[str, Any]) -> None:
        pathname, search = to.split("?", 1) if "?" in to else (to, "")
        set_location(Location(pathname, search))

    attrs = {
        **attributes,
        "href": to,
        "onClick": on_click,
        "id": uuid,
    }
    return html._(html.a(attrs, *children), html.script(link_js_content.replace("UUID", uuid)))


def use_params() -> dict[str, Any]:
    """The `use_params` hook returns an object of key/value pairs of the dynamic params \
    from the current URL that were matched by the `Route`. Child routes inherit all params \
    from their parent routes.

    For example, if you have a `URL_PARAM` defined in the route `/example/<URL_PARAM>/`,
    this hook will return the URL_PARAM value that was matched."""

    # TODO: Check if this returns all parent params
    return _use_route_state().params


def use_search_params(
    keep_blank_values: bool = False,
    strict_parsing: bool = False,
    errors: str = "replace",
    max_num_fields: int | None = None,
    separator: str = "&",
) -> dict[str, list[str]]:
    """
    The `use_search_params` hook is used to read and modify the query string in the URL \
    for the current location. Like React's own `use_state` hook, `use_search_params returns \
    an array of two values: the current location's search params and a function that may \
    be used to update them.

    See `urllib.parse.parse_qs` for info on this hook's parameters."""

    # FIXME: This needs to return a tuple of the search params and a function to update them
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
            matches.append(match)

    if not matches:
        _logger.debug("No matching route found for %s", location.pathname)

    return matches


History = export(
    module_from_file("reactpy-router", file=Path(__file__).parent / "static" / "bundle.js"),
    ("History"),
)
link_js_content = (Path(__file__).parent / "static" / "link.js").read_text(encoding="utf-8")


@dataclass
class _RouteState:
    set_location: Callable[[Location], None]
    params: dict[str, Any]


def _use_route_state() -> _RouteState:
    route_state = use_context(_route_state_context)
    if route_state is None:
        raise RuntimeError(
            "ReactPy-Router was unable to find a route context. Are you "
            "sure this hook/component is being called within a router?"
        )

    return route_state


_route_state_context: Context[_RouteState | None] = create_context(None)
