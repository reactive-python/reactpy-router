# Changelog

All notable changes to this project will be documented in this file.

<!--attr-start-->

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--attr-end-->

<!--
Using the following categories, list your changes in this order:

### Added
-   for new features.

### Changed
-   for changes in existing functionality.

### Deprecated
-   for soon-to-be removed features.

### Removed
-   for removed features.

### Fixed
-   for bug fixes.

### Security
-   for vulnerability fixes.
 -->

<!--changelog-start-->

## [Unreleased]

### Changed

-   Bump GitHub workflows
-   Rename `use_query` to `use_search_params`.
-   Rename `simple.router` to `browser_router`.
-   Rename `SimpleResolver` to `StarletteResolver`.
-   Rename `CONVERSION_TYPES` to `CONVERTERS`.
-   Change "Match Any" syntax from a star `*` to `{name:any}`.
-   Rewrite `reactpy_router.link` to be a server-side component.
-   Simplified top-level exports within `reactpy_router`.

### Added

-   New error for ReactPy router elements being used outside router context.
-   Configurable/inheritable `Resolver` base class.
-   Add debug log message for when there are no router matches.
-   Add slug as a supported type.

### Fixed

-   Fix bug where changing routes could cause render failure due to key identity.
-   Fix bug where "Match Any" pattern wouldn't work when used in complex or nested paths.
-   Fix bug where `link` elements could not have `@component` type children.
-   Fixed flakey tests being flakey on GitHub CI by adding click delays.

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

[Unreleased]: https://github.com/reactive-python/reactpy-router/compare/0.1.1...HEAD
[0.1.1]: https://github.com/reactive-python/reactpy-router/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/reactive-python/reactpy-router/compare/0.0.1...0.1.0
[0.0.1]: https://github.com/reactive-python/reactpy-router/releases/tag/0.0.1
