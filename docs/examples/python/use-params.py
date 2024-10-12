from reactpy import component, html, run

from reactpy_router import browser_router, link, route, use_params


@component
def user():
    params = use_params()
    return html._(html.h1(f"User {params['id']} 👤"), html.p("Nothing (yet)."))


@component
def root():
    return browser_router(
        route(
            "/",
            html.div(
                html.h1("Home Page 🏠"),
                link({"to": "/user/123"}, "User 123"),
            ),
        ),
        route("/user/{id:int}", user()),
    )


run(root)
