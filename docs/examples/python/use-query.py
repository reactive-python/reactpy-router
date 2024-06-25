from reactpy import component, html
from reactpy_router import browser_router, link, route, use_search_params


@component
def search():
    query = use_search_params()
    return html.h1(f"Search Results for {query['q'][0]} 🔍")


@component
def root():
    return browser_router(
        route(
            "/",
            html.div(
                html.h1("Home Page 🏠"),
                link("Search", to="/search?q=reactpy"),
            ),
        ),
        route("/about", html.h1("About Page 📖")),
    )
