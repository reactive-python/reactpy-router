from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin
from uuid import uuid4

from reactpy import component, html, use_connection
from reactpy.backend.types import Location
from reactpy.web.module import export, module_from_file

from reactpy_router.hooks import _use_route_state
from reactpy_router.types import Route

if TYPE_CHECKING:
    from reactpy.core.component import Component
    from reactpy.core.types import Key, VdomDict

History = export(
    module_from_file("reactpy-router", file=Path(__file__).parent / "static" / "bundle.js"),
    ("History"),
)
"""Client-side portion of history handling"""

Link = export(
    module_from_file("reactpy-router", file=Path(__file__).parent / "static" / "bundle.js"),
    ("Link"),
)
"""Client-side portion of link handling"""

Navigate = export(
    module_from_file("reactpy-router", file=Path(__file__).parent / "static" / "bundle.js"),
    ("Navigate"),
)
"""Client-side portion of the navigate component"""

FirstLoad = export(
    module_from_file("reactpy-router", file=Path(__file__).parent / "static" / "bundle.js"),
    ("FirstLoad"),
)

link_js_content = (Path(__file__).parent / "static" / "link.js").read_text(encoding="utf-8")


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
    uuid_string = f"link-{uuid4().hex}"
    class_name = f"{uuid_string}"
    set_location = _use_route_state().set_location
    if "className" in attributes:
        class_name = " ".join([attributes.pop("className"), class_name])
    if "class_name" in attributes:  # pragma: no cover
        # TODO: This can be removed when ReactPy stops supporting underscores in attribute names
        class_name = " ".join([attributes.pop("class_name"), class_name])
    if "href" in attributes and "to" not in attributes:
        attributes["to"] = attributes.pop("href")
    if "to" not in attributes:  # pragma: no cover
        msg = "The `to` attribute is required for the `Link` component."
        raise ValueError(msg)
    to = attributes.pop("to")

    attrs = {
        **attributes,
        "href": to,
        "className": class_name,
    }

    # FIXME: This component currently works in a "dumb" way by trusting that ReactPy's script tag \
    # properly sets the location due to bugs in ReactPy rendering.
    # https://github.com/reactive-python/reactpy/pull/1224
    current_path = use_connection().location.pathname

    def on_click(_event: dict[str, Any]) -> None:
        if _event.get("ctrlKey", False):
            return

        pathname, search = to.split("?", 1) if "?" in to else (to, "")
        if search:
            search = f"?{search}"

        # Resolve relative paths that match `../foo`
        if pathname.startswith("../"):
            pathname = urljoin(current_path, pathname)

        # Resolve relative paths that match `foo`
        if not pathname.startswith("/"):
            pathname = urljoin(current_path, pathname)

        # Resolve relative paths that match `/foo/../bar`
        while "/../" in pathname:
            part_1, part_2 = pathname.split("/../", 1)
            pathname = urljoin(f"{part_1}/", f"../{part_2}")

        # Resolve relative paths that match `foo/./bar`
        pathname = pathname.replace("/./", "/")

        set_location(Location(pathname, search))

    attrs["onClick"] = on_click

    return html._(html.a(attrs, *children), html.script(link_js_content.replace("UUID", uuid_string)))

    # def on_click_callback(_event: dict[str, Any]) -> None:
    #     set_location(Location(**_event))
    # return html._(html.a(attrs, *children), Link({"onClickCallback": on_click_callback, "linkClass": uuid_string}))


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


def navigate(to: str, replace: bool = False, key: Key | None = None) -> Component:
    """
    Navigate to a specified URL.

    This function changes the browser's current URL when it is rendered.

    Args:
        to: The target URL to navigate to.
        replace: If True, the current history entry will be replaced \
            with the new URL. Defaults to False.

    Returns:
        The component responsible for navigation.
    """
    return _navigate(to, replace, key=key)


@component
def _navigate(to: str, replace: bool = False) -> VdomDict | None:
    location = use_connection().location
    set_location = _use_route_state().set_location
    pathname = to.split("?", 1)[0]

    def on_navigate_callback(_event: dict[str, Any]) -> None:
        set_location(Location(**_event))

    if location.pathname != pathname:
        return Navigate({"onNavigateCallback": on_navigate_callback, "to": to, "replace": replace})

    return None
