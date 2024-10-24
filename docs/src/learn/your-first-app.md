<p class="intro" markdown>

Here you'll learn the various features of `reactpy-router` and how to use them. These examples will utilize the [`reactpy_router.browser_router`][reactpy_router.browser_router].

</p>

!!! abstract "Note"

    These docs assume you already know the basics of [ReactPy](https://reactpy.dev).

---

Let's build a simple web application for viewing messages between several people.

For the purposes of this tutorial we'll be working with the following data.

```python linenums="0"
message_data = [
    {"id": 1, "with": ["Alice"], "from": None, "message": "Hello!"},
    {"id": 2, "with": ["Alice"], "from": "Alice", "message": "How's it going?"},
    {"id": 3, "with": ["Alice"], "from": None, "message": "Good, you?"},
    {"id": 4, "with": ["Alice"], "from": "Alice", "message": "Good, thanks!"},
    {"id": 5, "with": ["Alice", "Bob"], "from": None, "message": "We meeting now?"},
    {"id": 6, "with": ["Alice", "Bob"], "from": "Alice", "message": "Not sure."},
    {"id": 7, "with": ["Alice", "Bob"], "from": "Bob", "message": "I'm here!"},
    {"id": 8, "with": ["Alice", "Bob"], "from": None, "message": "Great!"},
]
```

In a more realistic application this data would be stored in a database, but for this tutorial we'll just keep it in memory.

## Creating Basic Routes

The first step is to create a basic router that will display the home page when the user navigates to the root of the application, and a "missing link" page for any other route.

=== "components.py"

    ```python
    {% include "../../examples/python/basic_routing.py" %}
    ```

When navigating to [`http://127.0.0.1:8000`](http://127.0.0.1:8000) you should see `Home Page 🏠`. However, if you go to any other route you will instead see `Missing Link 🔗‍💥`.

With this foundation you can start adding more routes.

=== "components.py"

    ```python
    {% include "../../examples/python/basic_routing_more_routes.py" %}
    ```

With this change you can now also go to [`/messages`](http://127.0.0.1:8000/messages) to see `Messages 💬`.

## Using Route Links

Instead of using the standard `#!python reactpy.html.a` element to create links to different parts of your application, use `#!python reactpy_router.link` instead. When users click links constructed using `#!python reactpy_router.link`, ReactPy will handle the transition and prevent a full page reload.

=== "components.py"

    ```python
    {% include "../../examples/python/route_links.py" %}
    ```

Now, when you go to the home page, you can click `Messages` link to go to [`/messages`](http://127.0.0.1:8000/messages).

## Adding Nested Routes

Routes can be nested in order to construct more complicated application structures.

=== "components.py"

    ```python
    {% include "../../examples/python/nested_routes.py" %}
    ```

## Adding Route Parameters

In the example above we had to manually create a `#!python messages_with(...)` component for each conversation. This would be better accomplished by defining a single route that declares route parameters instead.

Any parameters that have matched in the currently displayed route can then be consumed with the `#!python use_params` hook which returns a dictionary mapping the parameter names to their values. Note that parameters with a declared type will be converted to is in the parameters dictionary. So for example `#!python /my/route/{my_param:float}` would match `#!python /my/route/3.14` and have a parameter dictionary of `#!python {"my_param": 3.14}`.

If we take this information and apply it to our growing example application we'd substitute the manually constructed `#!python /messages/with` routes with a single `#!python /messages/with/{names}` route.

=== "components.py"

    ```python
    {% include "../../examples/python/route_parameters.py" %}
    ```
