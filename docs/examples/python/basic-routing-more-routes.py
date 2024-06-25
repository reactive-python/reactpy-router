from reactpy import component, html, run
from reactpy_router import browser_router, route


@component
def root():
    return browser_router(
        route("/", html.h1("Home Page 🏠")),
        route("/messages", html.h1("Messages 💬")),
        route("*", html.h1("Missing Link 🔗‍💥")),
    )


run(root)
