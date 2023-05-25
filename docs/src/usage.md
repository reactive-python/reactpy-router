# Usage

!!! note

    The sections below assume you already know the basics of [ReacPy](https://reactpy.dev).

Here you'll learn the various features of `reactpy-router` and how to use them. All examples
will utilize the [simple.router][reactpy_router.simple.router] (though you can [use your own](#custom-routers)).

## Routers and Routes

The [simple.router][reactpy_router.simple.router] component is one possible
implementation of a [Router][reactpy_router.types.Router]. Routers takes a series of
[Route][reactpy_router.types.Route] objects as positional arguments and render whatever
element matches the current location. For convenience, these `Route` objects are created
using the [route][reactpy_router.route] function.

!!! note

    The current location is determined based on the browser's current URL and can be found
    by checking the [use_location][reactpy.backend.hooks.use_location] hook.

Here's a basic example showing how to use `simple.router` with two routes:

```python
from reactpy import component, html, run
from reactpy_router import route, simple, use_location

@component
def root():
    location = use_location()
    return simple.router(
        route("/", html.h1("Home Page 🏠")),
        route("*", html.h1("Missing Link 🔗‍💥")),
    )
```

Here we'll note some special syntax in the route path for the second route. The `*` is a
wildcard that will match any path. This is useful for creating a "404" page that will be
shown when no other route matches.

### Simple Router

The syntax for declaring routes with the [simple.router][reactpy_router.simple.router]
is very similar to the syntax used by [Starlette](https://www.starlette.io/routing/) (a
popular Python web framework). As such route parameters are declared using the following
syntax:

```
/my/route/{param}
/my/route/{param:type}
```

In this case, `param` is the name of the route parameter and the optionally declared
`type` specifies what kind of parameter it is. The available parameter types and what
patterns they match are are:

- str (default) - `[^/]+`
- int - `\d+`
- float - `\d+(\.\d+)?`
- uuid - `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`
- path - `.+`

!!! note

    The `path` type is special in that it will match any path, including `/` characters.
    This is useful for creating routes that match a path prefix.

So in practice these each might look like:

```
/my/route/{param}
/my/route/{param:int}
/my/route/{param:float}
/my/route/{param:uuid}
/my/route/{param:path}
```

Any route parameters collected from the current location then be accessed using the
[`use_params`](#using-parameters) hook.

!!! note

    It's worth pointing out that, while you can use route parameters to capture values
    from queryies (i.e. `?foo=bar`), this is not recommended. Instead, you should use
    the [use_query][reactpy_router.use_query] hook to access query parameters.

### Route Links

Links between routes should be created using the [link][reactpy_router.link] component.
This will allow ReactPy to handle the transition between routes more quickly by avoiding
the cost of a full page load.

```python
from reactpy import component, html, run
from reactpy_router import link, route, simple, use_location

@component
def root():
    location = use_location()
    return simple.router(
        route("/", html.h1("Home Page 🏠")),
        route("/about", html.h1("About Page 📖")),
        link("/about", html.button("About")),
    )
```

## Hooks

`reactpy-router` provides a number of hooks for working with the routes:

- [`use_query`](#using-queries) - for accessing query parameters
- [`use_params`](#using-parameters) - for accessing route parameters

If you're not familiar with hooks, you should
[read the docs](https://reactpy.dev/docs/guides/adding-interactivity/components-with-state/index.html#your-first-hook).

### Using Queries

The [use_query][reactpy_router.use_query] hook can be used to access query parameters
from the current location. It returns a dictionary of query parameters, where each value
is a list of strings.

```python
from reactpy import component, html, run
from reactpy_router import link, route, simple, use_query

@component
def root():
    return simple.router(
        route("/", html.h1("Home Page 🏠")),
        route("/search", search()),
        link("Search", to="/search?q=reactpy"),
    )

@component
def search():
    query = use_query()
    return html.h1(f"Search Results for {query['q'][0]} 🔍")
```

### Using Parameters

The [use_params][reactpy_router.use_params] hook can be used to access route parameters
from the current location. It returns a dictionary of route parameters, where each value
is mapped to a value that matches the type specified in the route path.

```python
from reactpy import component, html, run
from reactpy_router import link, route, simple, use_params

@component
def root():
    return simple.router(
        route("/", html.h1("Home Page 🏠")),
        route("/user/{id:int}", user()),
        link("User 123", to="/user/123"),
    )

@component
def user():
    params = use_params()
    return html.h1(f"User {params['id']} 👤")
```
