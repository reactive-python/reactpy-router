Several pre-fabricated hooks are provided to help integrate with routing features. You can learn more about them below.

!!! abstract "Note"

    If you're not familiar what a hook is, you should [read the ReactPy docs](https://reactpy.dev/docs/guides/adding-interactivity/components-with-state/index.html#your-first-hook).

---

## Use Query

The [`use_query`][reactpy_router.use_query] hook can be used to access query parameters from the current location. It returns a dictionary of query parameters, where each value is a list of strings.

=== "components.py"

    ```python
    {% include "../../examples/python/use-query.py" %}
    ```

## Use Params

The [`use_params`][reactpy_router.use_params] hook can be used to access route parameters from the current location. It returns a dictionary of route parameters, where each value is mapped to a value that matches the type specified in the route path.

=== "components.py"

    ```python
    {% include "../../examples/python/use-params.py" %}
    ```
