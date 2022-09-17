from __future__ import annotations

import re
from dataclasses import dataclass
from fnmatch import translate as fnmatch_translate
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence

from idom import component, create_context, use_context, use_state
from idom.core.types import VdomAttributesAndChildren, VdomDict
from idom.core.vdom import coalesce_attributes_and_children
from idom.types import BackendImplementation, ComponentType, Context, Location
from idom.web.module import export, module_from_file

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol


class Routes(Protocol):
    def __call__(self, *routes: Route) -> ComponentType:
        ...


def configure(
    implementation: BackendImplementation[Any] | Callable[[], Location]
) -> Routes:
    if isinstance(implementation, BackendImplementation):
        use_location = implementation.use_location
    elif callable(implementation):
        use_location = implementation
    else:
        raise TypeError(
            "Expected a BackendImplementation or "
            f"`use_location` hook, not {implementation}"
        )

    @component
    def Router(*routes: Route) -> ComponentType | None:
        initial_location = use_location()
        location, set_location = use_state(initial_location)
        for p, r in _compile_routes(routes):
            match = p.match(location.pathname)
            if match:
                return _LocationStateContext(
                    r.element,
                    value=_LocationState(location, set_location, match),
                    key=p.pattern,
                )
        return None

    return Router


def use_location() -> Location:
    return _use_location_state().location


def use_match() -> re.Match[str]:
    return _use_location_state().match


@dataclass
class Route:
    path: str | re.Pattern[str]
    element: Any


@component
def Link(*attributes_or_children: VdomAttributesAndChildren, to: str) -> VdomDict:
    attributes, children = coalesce_attributes_and_children(attributes_or_children)
    set_location = _use_location_state().set_location
    attrs = {
        **attributes,
        "to": to,
        "onClick": lambda event: set_location(Location(**event)),
    }
    return _Link(attrs, *children)


def _compile_routes(routes: Sequence[Route]) -> Iterator[tuple[re.Pattern[str], Route]]:
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


@dataclass
class _LocationState:
    location: Location
    set_location: Callable[[Location], None]
    match: re.Match[str]


_LocationStateContext: Context[_LocationState | None] = create_context(None)

_Link = export(
    module_from_file(
        "idom-router",
        file=Path(__file__).parent / "bundle.js",
        fallback="⏳",
    ),
    "Link",
)
