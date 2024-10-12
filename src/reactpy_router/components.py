from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from reactpy import component, html
from reactpy.backend.types import Location
from reactpy.core.types import VdomDict
from reactpy.web.module import export, module_from_file

from reactpy_router.hooks import _use_route_state
from reactpy_router.types import Route

History = export(
    module_from_file("reactpy-router", file=Path(__file__).parent / "static" / "bundle.js"),
    ("History"),
)
Link = export(
    module_from_file("reactpy-router", file=Path(__file__).parent / "static" / "bundle.js"),
    ("Link"),
)


@component
def link(*attributes_and_children: Any, to: str | None = None, **kwargs: Any) -> VdomDict:
    """A component that renders a link to the given path."""
    if to is None:
        raise ValueError("The `to` attribute is required for the `Link` component.")

    uuid_string = f"link-{uuid4().hex}"
    class_name = f"{uuid_string}"
    set_location = _use_route_state().set_location
    attributes = {}
    children: tuple[Any] = attributes_and_children

    if attributes_and_children and isinstance(attributes_and_children[0], dict):
        attributes = attributes_and_children[0]
        children = attributes_and_children[1:]
    if "className" in attributes:
        class_name = " ".join([attributes.pop("className"), class_name])
    if "class_name" in attributes:  # pragma: no cover
        # TODO: This can be removed when ReactPy stops supporting underscores in attribute names
        class_name = " ".join([attributes.pop("class_name"), class_name])

    attrs = {
        **attributes,
        "href": to,
        "className": class_name,
    }

    def on_click(_event: dict[str, Any]) -> None:
        set_location(Location(**_event))

    return html._(html.a(attrs, *children, **kwargs), Link({"onClick": on_click, "linkClass": uuid_string}))


def route(path: str, element: Any | None, *routes: Route) -> Route:
    """Create a route with the given path, element, and child routes."""
    return Route(path, element, routes)
