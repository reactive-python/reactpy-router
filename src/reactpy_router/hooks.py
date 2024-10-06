from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import parse_qs

from reactpy import (
    create_context,
    use_context,
    use_location,
)
from reactpy.backend.types import Location
from reactpy.types import Context


@dataclass
class _RouteState:
    set_location: Callable[[Location], None]
    params: dict[str, Any]


def _use_route_state() -> _RouteState:
    route_state = use_context(_route_state_context)
    if route_state is None:  # pragma: no cover
        raise RuntimeError(
            "ReactPy-Router was unable to find a route context. Are you "
            "sure this hook/component is being called within a router?"
        )

    return route_state


_route_state_context: Context[_RouteState | None] = create_context(None)


def use_params() -> dict[str, Any]:
    """The `use_params` hook returns an object of key/value pairs of the dynamic parameters \
    from the current URL that were matched by the `Route`. Child routes inherit all parameters \
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
    for the current location. Like React's own `use_state` hook, `use_search_params` returns \
    an array of two values: the current location's search parameters and a function that may \
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
