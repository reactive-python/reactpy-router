from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from reactpy import component, html
from reactpy.backend.types import Location
from reactpy.core.types import VdomChild, VdomDict
from reactpy.web.module import export, module_from_file

from reactpy_router.hooks import _use_route_state
from reactpy_router.types import Route

History = export(
    module_from_file("reactpy-router", file=Path(__file__).parent / "static" / "bundle.js"),
    ("History"),
)
link_js_content = (Path(__file__).parent / "static" / "link.js").read_text(encoding="utf-8")


@component
def link(*children: VdomChild, to: str, **attributes: Any) -> VdomDict:
    """A component that renders a link to the given path."""
    # FIXME: This currently works in a "dumb" way by trusting that ReactPy's script tag \
    # properly sets the location. When a client-server communication layer is added to a \
    # future ReactPy release, this component will need to be rewritten to use that instead. \
    set_location = _use_route_state().set_location
    class_uuid = f"link-{uuid4().hex}"

    def on_click(_event: dict[str, Any]) -> None:
        pathname, search = to.split("?", 1) if "?" in to else (to, "")
        if search:
            search = f"?{search}"
        set_location(Location(pathname, search))

    class_name = class_uuid
    if "className" in attributes:
        class_name = " ".join([attributes.pop("className"), class_name])
    # TODO: This can be removed when ReactPy stops supporting underscores in attribute names
    if "class_name" in attributes:  # pragma: no cover
        class_name = " ".join([attributes.pop("class_name"), class_name])

    attrs = {
        **attributes,
        "href": to,
        "onClick": on_click,
        "className": class_uuid,
    }
    return html._(html.a(attrs, *children), html.script(link_js_content.replace("UUID", class_uuid)))


def route(path: str, element: Any | None, *routes: Route) -> Route:
    """Create a route with the given path, element, and child routes."""
    return Route(path, element, routes)
