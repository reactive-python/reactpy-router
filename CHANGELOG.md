# Changelog

All notable changes to this project will be documented in this file.

<!--attr-start-->

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--attr-end-->

<!--
Using the following categories, list your changes in this order:
[Added, Changed, Deprecated, Removed, Fixed, Security]

Don't forget to remove deprecated code on each major release!
-->

<!--changelog-start-->

## [Unreleased]

-   Nothing (yet)!

## [2.0.0] - 2025-06-14

### Added

-   Support for custom routers.

### Changed

-   Set maximum ReactPy version to `<2.0.0`.
-   Set minimum ReactPy version to `1.1.0`.
-   `link` element now calculates URL changes using the client.
-   Refactoring related to `reactpy>=1.1.0` changes.
-   Changed ReactPy-Router's method of waiting for the initial URL to be deterministic.
-   Rename `StarletteResolver` to `ReactPyResolver`.

### Removed

-   `StarletteResolver` is removed in favor of `ReactPyResolver`.

### Fixed

-   Fixed bug where `link` element sometimes would sometimes not retrieve the correct `href` attribute.

## [1.0.3] - 2024-11-21

### Fixed

-   Fix behavior where the page would be rendered twice on initial load

## [1.0.2] - 2024-10-24

### Fixed

-   Fix python `wheel` missing `bundle.js` file.

## [1.0.1] - 2024-10-24

### Changed

-   JavaScript bundle is now created using [`Bun`](https://bun.sh/).
-   Python package is now built using [`Hatch`](https://hatch.pypa.io/).

## [1.0.0] - 2024-10-18

### Changed

-   Rename `use_query` to `use_search_params`.
-   Rename `simple.router` to `browser_router`.
-   Rename `SimpleResolver` to `StarletteResolver`.
-   Rename `CONVERSION_TYPES` to `CONVERTERS`.
-   Change "Match Any" syntax from a star `*` to `{name:any}`.
-   Rewrite `reactpy_router.link` to be a server-side component.
-   Simplified top-level exports that are available within `reactpy_router.*`.

### Added

-   Add debug log message for when there are no router matches.
-   Add slug as a supported type.
-   Add `reactpy_router.navigate` component that will force the client to navigate to a new URL (when rendered).
-   New error for ReactPy router elements being used outside router context.
-   Configurable/inheritable `Resolver` base class.

### Fixed

-   Fix bug where changing routes could cause render failure due to key identity.
-   Fix bug where "Match Any" pattern wouldn't work when used in complex or nested paths.
-   Fix bug where `link` elements could not have `@component` type children.
-   Fix bug where the ReactPy would not detect the current URL after a reconnection.
-   Fix bug where `ctrl` + `click` on a `link` element would not open in a new tab.
-   Fix test suite on Windows machines.

## [0.1.1] - 2023-12-13

### Fixed

-   Fixed relative navigation.

## [0.1.0] - 2023-06-16

### Added

-   Automatically handle client-side history changes.

## [0.0.1] - 2023-05-10

### Added

-   Add robust lint/testing.
-   Upgrade `reactpy`.
-   More robust routing with `starlette`.
-   Initial draft of router compiler.

### Changed

-   Rename `configure` to `create_router`.
-   Rename from `idom-router` to `reactpy-router`.

[Unreleased]: https://github.com/reactive-python/reactpy-router/compare/2.0.0...HEAD
[2.0.0]: https://github.com/reactive-python/reactpy-router/compare/1.0.3...2.0.0
[1.0.3]: https://github.com/reactive-python/reactpy-router/compare/1.0.2...1.0.3
[1.0.2]: https://github.com/reactive-python/reactpy-router/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/reactive-python/reactpy-router/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/reactive-python/reactpy-router/compare/0.1.1...1.0.0
[0.1.1]: https://github.com/reactive-python/reactpy-router/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/reactive-python/reactpy-router/compare/0.0.1...0.1.0
[0.0.1]: https://github.com/reactive-python/reactpy-router/releases/tag/0.0.1
