from __future__ import annotations
from dataclasses import dataclass

from fnmatch import translate as fnmatch_translate
from pathlib import Path
import re
from typing import Any, Iterator, Protocol, Callable, Sequence

from idom import create_context, component, use_context, use_state
from idom.web.module import export, module_from_file
from idom.core.vdom import coalesce_attributes_and_children, VdomAttributesAndChildren
from idom.types import BackendImplementation, ComponentType, Context, Location


class Router(Protocol):
    def __call__(self, *routes: Route) -> ComponentType:
        ...


def bind(backend: BackendImplementation) -> Router:
    @component
    def Router(*routes: Route):
        initial_location = backend.use_location()
        location, set_location = use_state(initial_location)
        for p, r in _compile_routes(routes):
            if p.match(location.pathname):
                return _LocationStateContext(
                    r.element,
                    value=(location, set_location),
                    key=r.path,
                )
        return None

    return Router


def use_location() -> str:
    return _use_location_state()[0]


@dataclass
class Route:
    path: str | re.Pattern
    element: Any


@component
def Link(*attributes_or_children: VdomAttributesAndChildren, to: str) -> None:
    attributes, children = coalesce_attributes_and_children(attributes_or_children)
    set_location = _use_location_state()[1]
    return _Link(
        {
            **attributes,
            "to": to,
            "onClick": lambda event: set_location(Location(**event)),
        },
        *children,
    )


def _compile_routes(routes: Sequence[Route]) -> Iterator[tuple[re.Pattern, Route]]:
    for r in routes:
        if isinstance(r.path, re.Pattern):
            yield r.path, r
            continue
        if not r.path.startswith("/"):
            raise ValueError("Path pattern must begin with '/'")
        pattern = re.compile(fnmatch_translate(r.path))
        yield pattern, r


def _use_location_state() -> _LocationState:
    location_state = use_context(_LocationStateContext)
    assert location_state is not None, "No location state. Did you use a Router?"
    return location_state


_LocationSetter = Callable[[str], None]
_LocationState = tuple[Location, _LocationSetter]
_LocationStateContext: type[Context[_LocationState | None]] = create_context(None)

_Link = export(
    module_from_file(
        "idom-router",
        file=Path(__file__).parent / "bundle.js",
        fallback="⏳",
    ),
    "Link",
)
