# reactpy-router

A URL router for ReactPy

# Installation

Use `pip` to install this package:

```bash
pip install reactpy-router
```

For a developer installation from source be sure to install [NPM](https://www.npmjs.com/) before running:

```bash
git clone https://github.com/reactive-python/reactpy-router
cd reactpy-router
pip install -e . -r requirements.txt
```

# Usage

Assuming you are familiar with the basics of [ReactPy](https://reactpy.dev), you can
begin by using the simple built-in router implementation supplied by `reactpy-router`.

```python
from reactpy import component, html, run
from reactpy_router import route, simple

@component
def root():
    return simple.router(
        route("/", html.h1("Home Page 🏠")),
        route("*", html.h1("Missing Link 🔗‍💥")),
    )

run(root)
```

When navigating to http://127.0.0.1:8000 you should see "Home Page 🏠". However, if you
go to any other route (e.g. http://127.0.0.1:8000/missing) you will instead see the
"Missing Link 🔗‍💥" page.

With this foundation you can start adding more routes:

```python
from reactpy import component, html, run
from reactpy_router import route, simple

@component
def root():
    return simple.router(
        route("/", html.h1("Home Page 🏠")),
        route("/messages", html.h1("Messages 💬")),
        route("*", html.h1("Missing Link 🔗‍💥")),
    )

run(root)
```

With this change you can now also go to `/messages` to see "Messages 💬" displayed.

# Route Links

Instead of using the standard `<a>` element to create links to different parts of your
application, use `reactpy_router.link` instead. When users click links constructed using
`reactpy_router.link`, instead of letting the browser navigate to the associated route,
ReactPy will more quickly handle the transition by avoiding the cost of a full page
load.

```python
from reactpy import component, html, run
from reactpy_router import link, route, simple

@component
def root():
    return simple.router(
        route("/", home()),
        route("/messages", html.h1("Messages 💬")),
        route("*", html.h1("Missing Link 🔗‍💥")),
    )

@component
def home():
    return html.div(
        html.h1("Home Page 🏠"),
        link("Messages", to="/messages"),
    )

run(root)
```

Now, when you go to the home page, you can click the link to go to `/messages`.

## Nested Routes

Routes can be nested in order to construct more complicated application structures:

```python
from reactpy import component, html, run
from reactpy_router import route, simple, link

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

@component
def root():
    return simple.router(
        route("/", home()),
        route(
            "/messages",
            all_messages(),
            # we'll improve upon these manually created routes in the next section...
            route("/with/Alice", messages_with("Alice")),
            route("/with/Alice-Bob", messages_with("Alice", "Bob")),
        ),
        route("*", html.h1("Missing Link 🔗‍💥")),
    )

@component
def home():
    return html.div(
        html.h1("Home Page 🏠"),
        link("Messages", to="/messages"),
    )

@component
def all_messages():
    last_messages = {
        ", ".join(msg["with"]): msg
        for msg in sorted(message_data, key=lambda m: m["id"])
    }
    return html.div(
        html.h1("All Messages 💬"),
        html.ul(
            [
                html.li(
                    {"key": msg["id"]},
                    html.p(
                        link(
                            f"Conversation with: {', '.join(msg['with'])}",
                            to=f"/messages/with/{'-'.join(msg['with'])}",
                        ),
                    ),
                    f"{'' if msg['from'] is None else '🔴'} {msg['message']}",
                )
                for msg in last_messages.values()
            ]
        ),
    )

@component
def messages_with(*names):
    names = set(names)
    messages = [msg for msg in message_data if set(msg["with"]) == names]
    return html.div(
        html.h1(f"Messages with {', '.join(names)} 💬"),
        html.ul(
            [
                html.li(
                    {"key": msg["id"]},
                    f"{msg['from'] or 'You'}: {msg['message']}",
                )
                for msg in messages
            ]
        ),
    )

run(root)
```

## Route Parameters

In the example above we had to manually create a `messages_with(...)` component for each
conversation. This would be better accomplished by defining a single route that declares
a "route parameters" instead. With the `simple.router` route parameters are declared
using the following syntax:

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

Any parameters that have matched in the currently displayed route can then be consumed
with the `use_params` hook which returns a dictionary mapping the parameter names to
their values. Note that parameters with a declared type will be converted to is in the
parameters dictionary. So for example `/my/route/{my_param:float}` would match
`/my/route/3.14` and have a parameter dictionary of `{"my_param": 3.14}`.

If we take this information and apply it to our growing example application we'd
substitute the manually constructed `/messages/with` routes with a single
`/messages/with/{names}` route:

```python
from reactpy import component, html, run
from reactpy_router import route, simple, link
from reactpy_router.core import use_params

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

@component
def root():
    return simple.router(
        route("/", home()),
        route(
            "/messages",
            all_messages(),
            route("/with/{names}", messages_with()),  # note the path param
        ),
        route("*", html.h1("Missing Link 🔗‍💥")),
    )

@component
def home():
    return html.div(
        html.h1("Home Page 🏠"),
        link("Messages", to="/messages"),
    )

@component
def all_messages():
    last_messages = {
        ", ".join(msg["with"]): msg
        for msg in sorted(message_data, key=lambda m: m["id"])
    }
    return html.div(
        html.h1("All Messages 💬"),
        html.ul(
            [
                html.li(
                    {"key": msg["id"]},
                    html.p(
                        link(
                            f"Conversation with: {', '.join(msg['with'])}",
                            to=f"/messages/with/{'-'.join(msg['with'])}",
                        ),
                    ),
                    f"{'' if msg['from'] is None else '🔴'} {msg['message']}",
                )
                for msg in last_messages.values()
            ]
        ),
    )

@component
def messages_with():
    names = set(use_params()["names"].split("-"))  # and here we use the path param
    messages = [msg for msg in message_data if set(msg["with"]) == names]
    return html.div(
        html.h1(f"Messages with {', '.join(names)} 💬"),
        html.ul(
            [
                html.li(
                    {"key": msg["id"]},
                    f"{msg['from'] or 'You'}: {msg['message']}",
                )
                for msg in messages
            ]
        ),
    )

run(root)
```

# Running the Tests

```bash
nox -s test
```

You can run the tests with a headed browser.

```bash
nox -s test -- --headed
```

# Releasing This Package

To release a new version of reactpy-router on PyPI:

1. Install [`twine`](https://twine.readthedocs.io/en/latest/) with `pip install twine`
2. Update the `version = "x.y.z"` variable in `reactpy-router/__init__.py`
3. `git` add the changes to `__init__.py` and create a `git tag -a x.y.z -m 'comment'`
4. Build the Python package with `python setup.py sdist bdist_wheel`
5. Check the build artifacts `twine check --strict dist/*`
6. Upload the build artifacts to [PyPI](https://pypi.org/) `twine upload dist/*`

To release a new version of `reactpy-router` on [NPM](https://www.npmjs.com/):

1. Update `js/package.json` with new npm package version
2. Clean out prior builds `git clean -fdx`
3. Install and publish `npm install && npm publish`
