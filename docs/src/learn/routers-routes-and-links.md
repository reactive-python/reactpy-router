We include built-in components that automatically handle routing, which enable Single Page Application (SPA) behavior.

---

## Routers and Routes

The [`simple.router`][src.reactpy_router.simple.router] component is one possible implementation of a [Router][src.reactpy_router.types.Router]. Routers takes a series of [route][src.reactpy_router.route] objects as positional arguments and render whatever element matches the current location.

!!! abstract "Note"

    The current location is determined based on the browser's current URL and can be found
    by checking the [`use_location`][reactpy.backend.hooks.use_location] hook.

Here's a basic example showing how to use `#!python simple.router` with two routes.

=== "components.py"

    ```python
    {% include "../../examples/python/basic-routing.py" %}
    ```

Here we'll note some special syntax in the route path for the second route. The `#!python "*"` is a wildcard that will match any path. This is useful for creating a "404" page that will be shown when no other route matches.

### Simple Router

The syntax for declaring routes with the [simple.router][src.reactpy_router.simple.router] is very similar to the syntax used by [`starlette`](https://www.starlette.io/routing/) (a popular Python web framework). As such route parameters are declared using the following syntax:

```python linenums="0"
/my/route/{param}
/my/route/{param:type}
```

In this case, `#!python param` is the name of the route parameter and the optionally declared `#!python type` specifies what kind of parameter it is. The available parameter types and what patterns they match are are:

| Type | Pattern |
| --- | --- |
| `#!python str` (default) | `#!python [^/]+` |
| `#!python int` | `#!python \d+` |
| `#!python float` | `#!python \d+(\.\d+)?` |
| `#!python uuid` | `#!python [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}` |
| `#!python path` | `#!python .+` |

So in practice these each might look like:

```python linenums="0"
/my/route/{param}
/my/route/{param:int}
/my/route/{param:float}
/my/route/{param:uuid}
/my/route/{param:path}
```

Any route parameters collected from the current location then be accessed using the [`use_params`](#using-parameters) hook.

!!! warning "Pitfall"

    While it is possible to use route parameters to capture values from query strings (such as `#!python /my/route/?foo={bar}`), this is not recommended. Instead, you should use the [`use_query`][src.reactpy_router.use_query] hook to access query string values.

## Route Links

Links between routes should be created using the [link][src.reactpy_router.link] component. This will allow ReactPy to handle the transition between routes and avoid a page reload.

=== "components.py"

    ```python
    {% include "../../examples/python/route-links.py" %}
    ```
