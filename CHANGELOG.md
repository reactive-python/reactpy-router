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

### Added

- Support for ReactPy v2.x (beta). The initial URL is now sourced from the ReactPy executor (`use_connection().location`) instead of a JS-side `popstate` effect, removing a redundant network round-trip on first load.

### Changed

- **Breaking:** Bumped minimum ReactPy version to `2.0.0b12`.
- **Breaking:** Migrated to Hatch `src/` layout — the package now lives at `src/reactpy_router/` (previously `reactpy_router/` at the repo root).
- **Breaking:** JavaScript build pipeline switched from Rollup (CommonJS) to Bun + TypeScript. The prebuilt bundle ships at `src/reactpy_router/static/bundle.js`.
- **Breaking:** Top-level re-exports trimmed. `Route`, `MatchedRoute`, `CompiledRoute`, `RouteState`, `ConversionInfo`, `ConverterMapping`, `Resolver`, and `Router` are no longer importable from `reactpy_router`. Import them from `reactpy_router.types` instead.
- **Breaking:** The `link` component no longer accepts the legacy underscore `class_name` attribute — use `className` only.
- **Breaking:** The internal `History` JavaScript callback was renamed from `onHistoryChangeCallback` to `onHistoryPreviousCallback` to reflect that it now fires only on browser history navigation events.
- `@reactpy/client` bumped to `^1.2.0`.
- The `uuid` route converter is now case-insensitive (previously matched only lowercase hex).

### Removed

- `StarletteResolver` and the `simple.py` / `core.py` modules that accompanied it (these were already removed in 2.0.0 in favor of `ReactPyResolver`; this release also drops the old `core.py`/`simple.py` modules).

## [2.0.0] - 2025-06-14

### Added

- Support for custom routers.

### Changed

- Set maximum ReactPy version to `<2.0.0`.
- Set minimum ReactPy version to `1.1.0`.
- `link` element now calculates URL changes using the client.
- Refactoring related to `reactpy>=1.1.0` changes.
- Changed ReactPy-Router's method of waiting for the initial URL to be deterministic.
- Rename `StarletteResolver` to `ReactPyResolver`.

### Removed

- `StarletteResolver` is removed in favor of `ReactPyResolver`.

### Fixed

- Fixed bug where `link` element sometimes would sometimes not retrieve the correct `href` attribute.

## [1.0.3] - 2024-11-21

### Fixed

- Fix behavior where the page would be rendered twice on initial load

## [1.0.2] - 2024-10-24

### Fixed

- Fix python `wheel` missing `bundle.js` file.

## [1.0.1] - 2024-10-24

### Changed

- JavaScript bundle is now created using [`Bun`](https://bun.sh/).
- Python package is now built using [`Hatch`](https://hatch.pypa.io/).

## [1.0.0] - 2024-10-18

### Changed

- Rename `use_query` to `use_search_params`.
- Rename `simple.router` to `browser_router`.
- Rename `SimpleResolver` to `StarletteResolver`.
- Rename `CONVERSION_TYPES` to `CONVERTERS`.
- Change "Match Any" syntax from a star `*` to `{name:any}`.
- Rewrite `reactpy_router.link` to be a server-side component.
- Simplified top-level exports that are available within `reactpy_router.*`.

### Added

- Add debug log message for when there are no router matches.
- Add slug as a supported type.
- Add `reactpy_router.navigate` component that will force the client to navigate to a new URL (when rendered).
- New error for ReactPy router elements being used outside router context.
- Configurable/inheritable `Resolver` base class.

### Fixed

- Fix bug where changing routes could cause render failure due to key identity.
- Fix bug where "Match Any" pattern wouldn't work when used in complex or nested paths.
- Fix bug where `link` elements could not have `@component` type children.
- Fix bug where the ReactPy would not detect the current URL after a reconnection.
- Fix bug where `ctrl` + `click` on a `link` element would not open in a new tab.
- Fix test suite on Windows machines.

## [0.1.1] - 2023-12-13

### Fixed

- Fixed relative navigation.

## [0.1.0] - 2023-06-16

### Added

- Automatically handle client-side history changes.

## [0.0.1] - 2023-05-10

### Added

- Add robust lint/testing.
- Upgrade `reactpy`.
- More robust routing with `starlette`.
- Initial draft of router compiler.

### Changed

- Rename `configure` to `create_router`.
- Rename from `idom-router` to `reactpy-router`.

[Unreleased]: https://github.com/reactive-python/reactpy-router/compare/2.0.0...HEAD
[2.0.0]: https://github.com/reactive-python/reactpy-router/compare/1.0.3...2.0.0
[1.0.3]: https://github.com/reactive-python/reactpy-router/compare/1.0.2...1.0.3
[1.0.2]: https://github.com/reactive-python/reactpy-router/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/reactive-python/reactpy-router/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/reactive-python/reactpy-router/compare/0.1.1...1.0.0
[0.1.1]: https://github.com/reactive-python/reactpy-router/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/reactive-python/reactpy-router/compare/0.0.1...0.1.0
[0.0.1]: https://github.com/reactive-python/reactpy-router/releases/tag/0.0.1
