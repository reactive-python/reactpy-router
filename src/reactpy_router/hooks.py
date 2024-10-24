from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs

from reactpy import create_context, use_context, use_location

from reactpy_router.types import RouteState  # noqa: TCH001

if TYPE_CHECKING:
    from reactpy.types import Context


_route_state_context: Context[RouteState | None] = create_context(None)


def _use_route_state() -> RouteState:
    route_state = use_context(_route_state_context)
    if route_state is None:  # pragma: no cover
        msg = (
            "ReactPy-Router was unable to find a route context. Are you "
            "sure this hook/component is being called within a router?"
        )
        raise RuntimeError(msg)

    return route_state


def use_params() -> dict[str, Any]:
    """This hook returns an object of key/value pairs of the dynamic parameters \
    from the current URL that were matched by the `Route`. Child routes inherit all parameters \
    from their parent routes.

    For example, if you have a `URL_PARAM` defined in the route `/example/<URL_PARAM>/`,
    this hook will return the `URL_PARAM` value that was matched.

    Returns:
        A dictionary of the current URL's parameters.
    """

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
    This hook is used to read the query string in the URL for the current location.

    See [`urllib.parse.parse_qs`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.parse_qs) \
        for info on this hook's parameters.

    Returns:
        A dictionary of the current URL's query string parameters.
    """
    location = use_location()
    query_string = location.search[1:] if len(location.search) > 1 else ""

    # TODO: In order to match `react-router`, this will need to return a tuple of the search params \
    # and a function to update them. This is currently not possible without reactpy core having a \
    # communication layer.
    return parse_qs(
        query_string,
        keep_blank_values=keep_blank_values,
        strict_parsing=strict_parsing,
        errors=errors,
        max_num_fields=max_num_fields,
        separator=separator,
    )
