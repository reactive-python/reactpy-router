Custom routers can be used to define custom routing logic for your application. This is useful when you need to implement a custom routing algorithm or when you need to integrate with an existing URL routing system.

---

## Step 1: Creating a custom resolver

You may want to create a custom resolver to allow ReactPy to utilize an existing routing syntax.

To start off, you will need to create a subclass of `#!python ReactPyResolver`. Within this subclass, you have two attributes which you can modify to support your custom routing syntax:

-   `#!python param_pattern`: A regular expression pattern that matches the parameters in your URL. This pattern must contain the regex named groups `name` and `type`.
-   `#!python converters`: A dictionary that maps a `type` to it's respective `regex` pattern and a converter `func`.

=== "resolver.py"

    ```python
    {% include "../../examples/python/custom_router_easy_resolver.py" %}
    ```

## Step 2: Creating a custom router

Then, you can use this resolver to create your custom router...

=== "resolver.py"

    ```python
    {% include "../../examples/python/custom_router_easy_router.py" %}
    ```
