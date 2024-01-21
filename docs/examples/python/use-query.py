from reactpy import component, html

from reactpy_router import link, route, simple, use_query


@component
def search():
    query = use_query()
    return html.h1(f"Search Results for {query['q'][0]} 🔍")


@component
def root():
    return simple.router(
        route(
            "/",
            html.div(
                html.h1("Home Page 🏠"),
                link("Search", to="/search?q=reactpy"),
            ),
        ),
        route("/about", html.h1("About Page 📖")),
    )
