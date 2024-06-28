from reactpy import component, html, run
from reactpy_router import browser_router, link, route


@component
def root():
    return browser_router(
        route("/", home()),
        route("/messages", html.h1("Messages 💬")),
        route("{404:any}", html.h1("Missing Link 🔗‍💥")),
    )


@component
def home():
    return html.div(
        html.h1("Home Page 🏠"),
        link("Messages", to="/messages"),
    )


run(root)
