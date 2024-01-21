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
