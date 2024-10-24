"""Type definitions for the `reactpy-router` package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, TypedDict, TypeVar

from reactpy.core.vdom import is_vdom
from typing_extensions import Protocol, Self, TypeAlias

if TYPE_CHECKING:
    from collections.abc import Sequence

    from reactpy.backend.types import Location
    from reactpy.core.component import Component
    from reactpy.types import Key

ConversionFunc: TypeAlias = Callable[[str], Any]
"""A function that converts a string to a specific type."""

ConverterMapping: TypeAlias = dict[str, ConversionFunc]
"""A mapping of conversion types to their respective functions."""


@dataclass(frozen=True)
class Route:
    """
    A class representing a route that can be matched against a path.

    Attributes:
        path (str): The path to match against.
        element (Any): The element to render if the path matches.
        routes (Sequence[Self]): Child routes.

    Methods:
        __hash__() -> int: Returns a hash value for the route based on its path, element, and child routes.
    """

    path: str
    element: Any = field(hash=False)
    routes: Sequence[Self]

    def __hash__(self) -> int:
        el = self.element
        key = el["key"] if is_vdom(el) and "key" in el else getattr(el, "key", id(el))
        return hash((self.path, key, self.routes))


RouteType = TypeVar("RouteType", bound=Route)
"""A type variable for `Route`."""

RouteType_contra = TypeVar("RouteType_contra", bound=Route, contravariant=True)
"""A contravariant type variable for `Route`."""


class Router(Protocol[RouteType_contra]):
    """Return a component that renders the matching route(s)."""

    def __call__(self, *routes: RouteType_contra) -> Component:
        """
        Process the given routes and return a component that renders the matching route(s).

        Args:
            *routes: A variable number of route arguments.

        Returns:
            The resulting component after processing the routes.
        """


class Resolver(Protocol[RouteType_contra]):
    """Compile a route into a resolver that can be matched against a given path."""

    def __call__(self, route: RouteType_contra) -> CompiledRoute:
        """
        Compile a route into a resolver that can be matched against a given path.

        Args:
            route: The route to compile.

        Returns:
            The compiled route.
        """


class CompiledRoute(Protocol):
    """
    A protocol for a compiled route that can be matched against a path.

    Attributes:
        key (Key): A property that uniquely identifies this resolver.
    """

    @property
    def key(self) -> Key: ...

    def resolve(self, path: str) -> tuple[Any, dict[str, Any]] | None:
        """
        Return the path's associated element and path parameters or None.

        Args:
            path (str): The path to resolve.

        Returns:
            A tuple containing the associated element and a dictionary of path parameters, or None if the path cannot be resolved.
        """


class ConversionInfo(TypedDict):
    """
    A TypedDict that holds information about a conversion type.

    Attributes:
        regex (str): The regex to match the conversion type.
        func (ConversionFunc): The function to convert the matched string to the expected type.
    """

    regex: str
    func: ConversionFunc


@dataclass
class RouteState:
    """
    Represents the state of a route in the application.

    Attributes:
        set_location: A callable to set the location.
        params: A dictionary containing route parameters.
    """

    set_location: Callable[[Location], None]
    params: dict[str, Any]
