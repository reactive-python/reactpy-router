from reactpy import component, html

from reactpy_router import link, route, simple, use_params


@component
def user():
    params = use_params()
    return html.h1(f"User {params['id']} 👤")


@component
def root():
    return simple.router(
        route(
            "/",
            html.div(
                html.h1("Home Page 🏠"),
                link("User 123", to="/user/123"),
            ),
        ),
        route("/user/{id:int}", user()),
    )
