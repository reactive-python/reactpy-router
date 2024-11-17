import pytest
from reactpy import component, html
from reactpy.testing import DisplayFixture

from reactpy_router import browser_router, route

from .utils import page_stable


@pytest.mark.anyio
async def test_router_simple(display: DisplayFixture):
    """Confirm the number of rendering operations when new pages are first loaded"""
    root_render_count = 0
    home_page_render_count = 0
    not_found_render_count = 0

    @component
    def root():
        nonlocal root_render_count
        root_render_count += 1

        @component
        def home_page():
            nonlocal home_page_render_count
            home_page_render_count += 1
            return html.h1("Home Page 🏠")

        @component
        def not_found():
            nonlocal not_found_render_count
            not_found_render_count += 1
            return html.h1("Missing Link 🔗‍💥")

        return browser_router(
            route("/", home_page()),
            route("{404:any}", not_found()),
        )

    await display.show(root)
    await page_stable(display.page)

    assert root_render_count == 1
    assert home_page_render_count == 1
    assert not_found_render_count == 0

    await display.goto("/xxx")
    await page_stable(display.page)

    assert root_render_count == 2
    assert home_page_render_count == 1
    assert not_found_render_count == 1

    await display.goto("/yyy")
    await page_stable(display.page)

    assert root_render_count == 3
    assert home_page_render_count == 1
    assert not_found_render_count == 2

    assert True
