from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from reactpy import component, html, use_connection, use_ref
from reactpy.reactjs import component_from_file
from reactpy.types import Location

from reactpy_router.hooks import _use_route_state
from reactpy_router.types import Route

if TYPE_CHECKING:
    from reactpy.types import Component, Key, VdomDict

History = component_from_file(
    Path(__file__).parent / "static" / "bundle.js", import_names="History", name="reactpy-router"
)
"""Client-side portion of history handling"""

Link = component_from_file(Path(__file__).parent / "static" / "bundle.js", import_names="Link", name="reactpy-router")
"""Client-side portion of link handling"""

Navigate = component_from_file(
    Path(__file__).parent / "static" / "bundle.js", import_names="Navigate", name="reactpy-router"
)
"""Client-side portion of the navigate component"""

ScrollRestoration = component_from_file(
    Path(__file__).parent / "static" / "bundle.js", import_names="ScrollRestoration", name="reactpy-router"
)
"""Client-side portion of scroll restoration"""


def link(attributes: dict[str, Any], *children: Any, key: Key | None = None) -> Component:
    """
    Create a link with the given attributes and children.

    Args:
        attributes: A dictionary of attributes for the link.
        *children: Child elements to be included within the link.

    Returns:
        A link component with the specified attributes and children.
    """
    return _link(attributes, *children, key=key)


@component
def _link(attributes: dict[str, Any], *children: Any) -> VdomDict:
    attributes = attributes.copy()
    class_name = use_ref(f"link-{uuid4().hex}").current
    set_location = _use_route_state().set_location
    if "className" in attributes:
        class_name = " ".join([attributes.pop("className"), class_name])
    if "href" in attributes and "to" not in attributes:
        attributes["to"] = attributes.pop("href")
    if "to" not in attributes:  # pragma: no cover
        msg = "The `to` attribute is required for the `link` component."
        raise ValueError(msg)
    to = attributes.pop("to")

    attrs = {
        **attributes,
        "href": to,
        "className": class_name,
    }

    def on_click_callback(_event: dict[str, Any]) -> None:
        set_location(Location(**_event))

    return html(Link({"onClickCallback": on_click_callback, "linkClass": class_name}), html.a(attrs, *children))


def route(path: str, element: Any | None, *routes: Route) -> Route:
    """
    Create a route with the given path, element, and child routes.

    Args:
        path: The path for the route.
        element: The element to render for this route. Can be None.
        routes: Additional child routes.

    Returns:
        The created route object.
    """
    return Route(path, element, routes)


def navigate(to: str | int, replace: bool = False, key: Key | None = None) -> Component:
    """
    Navigate to a specified URL.

    This function changes the browser's current URL when it is rendered.

    Args:
        to: The target URL to navigate to, or an integer indicating the relative
            position in the browser's history stack (e.g., ``-1`` to go back,
            ``1`` to go forward). See `History.go <https://developer.mozilla.org/en-US/docs/Web/API/History/go>`_.
        replace: If True, the current history entry will be replaced \
            with the new URL. Ignored when ``to`` is an integer. Defaults to False.

    Returns:
        The component responsible for navigation.
    """
    return _navigate(to, replace, key=key)


@component
def _navigate(to: str | int, replace: bool = False) -> VdomDict | None:
    location = use_connection().location
    set_location = _use_route_state().set_location

    def on_navigate_callback(_event: dict[str, Any]) -> None:
        set_location(Location(**_event))

    if isinstance(to, int):
        # Integer navigation (go back/forward) — always delegate to JS;
        # the resulting popstate event is handled by the History component.
        return Navigate({"onNavigateCallback": on_navigate_callback, "to": to, "replace": replace})

    if isinstance(to, str):
        new_path = to.split("?", 1)[0]
        if location.path != new_path:
            return Navigate({"onNavigateCallback": on_navigate_callback, "to": to, "replace": replace})

    return None


def scroll_restoration(*children: Any, key: Key | None = None) -> Component:
    """
    A component that saves and restores scroll positions across client-side navigation.

    This component is analogous to React Router's ``ScrollRestoration`` component.
    It renders a hidden JavaScript component that manages scroll positions by keying
    them to the current URL pathname. Scroll positions are automatically saved when
    navigating away from a page and restored when returning via browser back/forward
    or client-side navigation.

    This component also accepts server-side children, which are rendered as the
    content of a wrapper ``<div>``.

    Args:
        *children: Server-side child elements to render inside the scroll restoration wrapper.

    Returns:
        A component that renders children inside a scroll restoration wrapper div.
    """
    return _scroll_restoration(*children, key=key)


@component
def _scroll_restoration(*children: Any) -> VdomDict:
    return html.div(
        {"style": {"height": "100%"}},
        ScrollRestoration({}),
        *children,
    )
