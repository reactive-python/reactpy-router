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
