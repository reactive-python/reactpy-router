import os
from typing import Any

import pytest
from playwright.async_api._generated import Browser, Page
from reactpy import Ref, component, html, use_location, use_state
from reactpy.testing import DisplayFixture

from reactpy_router import browser_router, link, navigate, route, scroll_restoration, use_params, use_search_params

GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS", "").lower() == "true"
pytestmark = pytest.mark.anyio


async def test_simple_router(display: DisplayFixture):
    def make_location_check(path, *routes):
        name = path.lstrip("/").replace("/", "-")

        @component
        def check_location():
            assert use_location().path == path
            return html.h1({"id": name}, path)

        return route(path, check_location(), *routes)

    @component
    def sample():
        return browser_router(
            make_location_check("/a"),
            make_location_check("/b"),
            make_location_check("/c"),
        )

    await display.show(sample)

    for path, selector in [
        ("/a", "#a"),
        ("/b", "#b"),
        ("/c", "#c"),
    ]:
        await display.goto(path)
        await display.page.wait_for_selector(selector)

    await display.goto("/missing")

    root_element = await display.page.wait_for_selector("#app", state="attached")

    assert not await root_element.inner_html()


async def test_nested_routes(display: DisplayFixture):
    @component
    def sample():
        return browser_router(
            route(
                "/a",
                html.h1({"id": "a"}, "A"),
                route(
                    "/b",
                    html.h1({"id": "b"}, "B"),
                    route("/c", html.h1({"id": "c"}, "C")),
                ),
            ),
        )

    await display.show(sample)

    for path, selector in [
        ("/a", "#a"),
        ("/a/b", "#b"),
        ("/a/b/c", "#c"),
    ]:
        await display.goto(path)
        await display.page.wait_for_selector(selector)


async def test_navigate_with_link(display: DisplayFixture):
    render_count = Ref(0)

    @component
    def sample():
        render_count.current += 1
        return browser_router(
            route("/", link({"to": "/a", "id": "root"}, "Root")),
            route("/a", link({"to": "/b", "id": "a"}, "A")),
            route("/b", link({"to": "/c", "id": "b"}, "B")),
            route("/c", link({"to": "/default", "id": "c"}, "C")),
            route("{default:any}", html.h1({"id": "default"}, "Default")),
        )

    await display.show(sample)

    for link_selector in ["#root", "#a", "#b", "#c"]:
        link_ = await display.page.wait_for_selector(link_selector)
        await link_.click()

    await display.page.wait_for_selector("#default")

    # check that we haven't re-rendered the root component by clicking the link
    # (i.e. we are preventing default link behavior)
    assert render_count.current == 1


async def test_use_params(display: DisplayFixture):
    expected_params: dict[str, Any] = {}

    @component
    def check_params():
        assert use_params() == expected_params
        return html.h1({"id": "success"}, "success")

    @component
    def sample():
        return browser_router(
            route(
                "/first/{first:str}",
                check_params(),
                route(
                    "/second/{second:str}",
                    check_params(),
                    route(
                        "/third/{third:str}",
                        check_params(),
                    ),
                ),
            )
        )

    await display.show(sample)

    for path, _expected_params in [
        ("/first/1", {"first": "1"}),
        ("/first/1/second/2", {"first": "1", "second": "2"}),
        ("/first/1/second/2/third/3", {"first": "1", "second": "2", "third": "3"}),
    ]:
        expected_params = _expected_params
        await display.goto(path)
        await display.page.wait_for_selector("#success")


async def test_search_params(display: DisplayFixture):
    expected_query: dict[str, Any] = {}

    @component
    def check_query():
        assert use_search_params() == expected_query
        return html.h1({"id": "success"}, "success")

    @component
    def sample():
        return browser_router(route("/", check_query()))

    await display.show(sample)

    expected_query = {"hello": ["world"], "thing": ["1", "2"]}
    await display.goto("?hello=world&thing=1&thing=2")
    await display.page.wait_for_selector("#success")


async def test_browser_popstate(display: DisplayFixture):
    @component
    def sample():
        return browser_router(
            route("/", link({"to": "/a", "id": "root"}, "Root")),
            route("/a", link({"to": "/b", "id": "a"}, "A")),
            route("/b", link({"to": "/c", "id": "b"}, "B")),
            route("/c", link({"to": "/default", "id": "c"}, "C")),
            route("{default:any}", html.h1({"id": "default"}, "Default")),
        )

    await display.show(sample)

    link_selectors = ["#root", "#a", "#b", "#c"]

    for link_selector in link_selectors:
        link_ = await display.page.wait_for_selector(link_selector)
        await link_.click()

    await display.page.wait_for_selector("#default")

    link_selectors.reverse()
    for link_selector in link_selectors:
        await display.page.go_back()
        await display.page.wait_for_selector(link_selector)


async def test_relative_links(display: DisplayFixture):
    @component
    def sample():
        return browser_router(
            route("/", link({"to": "a", "id": "root"}, "Root")),
            route("/a", link({"to": "/a/a/../b", "id": "a"}, "A")),
            route("/a/b", link({"to": "../a/b/c", "id": "b"}, "B")),
            route("/a/b/c", link({"to": "../d", "id": "c"}, "C")),
            route("/a/d", link({"to": "e", "id": "d"}, "D")),
            route("/a/e", link({"to": "/a/./f", "id": "e"}, "E")),
            route("/a/f", link({"to": "../default", "id": "f"}, "F")),
            route("{default:any}", html.h1({"id": "default"}, "Default")),
        )

    await display.show(sample)

    selectors = ["#root", "#a", "#b", "#c", "#d", "#e", "#f"]

    for link_selector in selectors:
        link_ = await display.page.wait_for_selector(link_selector)
        await link_.click()

    await display.page.wait_for_selector("#default")

    selectors.reverse()
    for link_selector in selectors:
        await display.page.go_back()
        await display.page.wait_for_selector(link_selector)


async def test_link_with_query_string(display: DisplayFixture):
    @component
    def check_search_params():
        query = use_search_params()
        assert query == {"a": ["1"], "b": ["2"]}
        return html.h1({"id": "success"}, "success")

    @component
    def sample():
        return browser_router(
            route("/", link({"to": "/a?a=1&b=2", "id": "root"}, "Root")),
            route("/a", check_search_params()),
        )

    await display.show(sample)
    await display.page.wait_for_selector("#root")
    link_ = await display.page.wait_for_selector("#root")
    await link_.click()
    await display.page.wait_for_selector("#success")


async def test_link_class_name(display: DisplayFixture):
    @component
    def sample():
        return browser_router(route("/", link({"to": "/a", "id": "root", "className": "class1"}, "Root")))

    await display.show(sample)

    link_ = await display.page.wait_for_selector("#root")
    assert "class1" in await link_.get_attribute("class")


async def test_link_href(display: DisplayFixture):
    @component
    def sample():
        return browser_router(route("/", link({"href": "/a", "id": "root"}, "Root")))

    await display.show(sample)

    link_ = await display.page.wait_for_selector("#root")
    assert "/a" in await link_.get_attribute("href")


async def test_ctrl_click(display: DisplayFixture, browser: Browser):
    @component
    def sample():
        return browser_router(
            route("/", link({"to": "/a", "id": "root"}, "Root")),
            route("/a", link({"to": "/a", "id": "a"}, "a")),
        )

    await display.show(sample)

    link_ = await display.page.wait_for_selector("#root")
    await link_.click(modifiers=["Control"])
    browser_context = browser.contexts[0]
    if len(browser_context.pages) == 1:
        new_page: Page = await browser_context.wait_for_event("page")
    else:
        new_page: Page = browser_context.pages[-1]  # type: ignore[no-redef]
    await new_page.wait_for_selector("#a")


async def test_navigate_component(display: DisplayFixture):
    @component
    def navigate_btn():
        nav_url, set_nav_url = use_state("")

        return html.button(
            {"onClick": lambda _: set_nav_url("/a")},
            navigate(nav_url) if nav_url else "Click to navigate",
        )

    @component
    def sample():
        return browser_router(
            route("/", navigate_btn()),
            route("/a", html.h1({"id": "a"}, "A")),
        )

    await display.show(sample)
    button = await display.page.wait_for_selector("button")
    await button.click()
    await display.page.wait_for_selector("#a")
    await display.page.go_back()
    await display.page.wait_for_selector("button")


async def test_navigate_component_replace(display: DisplayFixture):
    @component
    def navigate_btn(to: str, replace: bool = False):
        nav_url, set_nav_url = use_state("")

        return html.button(
            {"onClick": lambda _: set_nav_url(to), "id": f"nav-{to.replace('/', '')}"},
            navigate(nav_url, replace) if nav_url else f"Navigate to {to}",
        )

    @component
    def sample():
        return browser_router(
            route("/", navigate_btn("/a")),
            route("/a", navigate_btn("/b", replace=True)),
            route("/b", html.h1({"id": "b"}, "B")),
        )

    await display.show(sample)
    button = await display.page.wait_for_selector("#nav-a")
    await button.click()
    button = await display.page.wait_for_selector("#nav-b")
    await button.click()
    await display.page.wait_for_selector("#b")
    await display.page.go_back()
    await display.page.wait_for_selector("#nav-a")


async def test_navigate_component_to_current_url(display: DisplayFixture):
    @component
    def navigate_btn(to: str, html_id: str):
        nav_url, set_nav_url = use_state("")

        return html.button(
            {"onClick": lambda _: set_nav_url(to), "id": html_id},
            navigate(nav_url) if nav_url else f"Navigate to {to}",
        )

    @component
    def sample():
        return browser_router(
            route("/", navigate_btn("/a", "root-a")),
            route("/a", navigate_btn("/a", "nav-a")),
        )

    await display.show(sample)
    button = await display.page.wait_for_selector("#root-a")
    await button.click()
    button = await display.page.wait_for_selector("#nav-a")
    await button.click()
    await display.page.wait_for_selector("#nav-a")
    await display.page.go_back()
    await display.page.wait_for_selector("#root-a")


async def test_navigate_component_go_back(display: DisplayFixture):
    """Navigate back using navigate(-1)."""

    @component
    def nav_btn():
        nav, set_nav = use_state("")

        if nav:
            return navigate(nav)

        return html.button(
            {"onClick": lambda _: set_nav("/a"), "id": "nav-to-a"},
            "Go to A",
        )

    @component
    def back_btn():
        delta, set_delta = use_state("")

        if isinstance(delta, int):
            return navigate(delta)

        return html.button(
            {"onClick": lambda _: set_delta(-1), "id": "go-back"},
            "Go back",
        )

    @component
    def sample():
        return browser_router(
            route("/", nav_btn()),
            route("/a", back_btn()),
        )

    await display.show(sample)

    # Navigate to /a
    await display.page.wait_for_selector("#nav-to-a")
    await display.page.click("#nav-to-a")

    # Wait for the go-back button to appear on route /a
    await display.page.wait_for_selector("#go-back")
    assert await display.page.text_content("#go-back") == "Go back"

    # Go back using navigate(-1)
    await display.page.click("#go-back")

    # Verify we're back at the root route
    await display.page.wait_for_selector("#nav-to-a")
    assert await display.page.text_content("#nav-to-a") == "Go to A"


async def test_navigate_component_go_forward(display: DisplayFixture):
    """Navigate forward using navigate(1)."""

    @component
    def forward_btn():
        delta, set_delta = use_state("")

        if isinstance(delta, int):
            return navigate(delta)

        return html.button(
            {"onClick": lambda _: set_delta(1), "id": "go-forward"},
            "Go forward",
        )

    @component
    def back_btn():
        delta, set_delta = use_state("")

        if isinstance(delta, int):
            return navigate(delta)

        return html.button(
            {"onClick": lambda _: set_delta(-1), "id": "go-back"},
            "Go back",
        )

    @component
    def sample():
        return browser_router(
            route("/", forward_btn()),
            route("/a", back_btn()),
        )

    await display.show(sample)

    # Navigate to /a via full page load (builds forward history entry)
    await display.goto("/a")

    # Go back to / via navigate(-1)
    await display.page.wait_for_selector("#go-back")
    await display.page.click("#go-back")

    # Should now be at / with the "Go forward" button
    await display.page.wait_for_selector("#go-forward")
    assert await display.page.text_content("#go-forward") == "Go forward"

    # Go forward to /a via navigate(1)
    await display.page.click("#go-forward")

    # Verify we're back at /a
    await display.page.wait_for_selector("#go-back")
    assert await display.page.text_content("#go-back") == "Go back"


async def test_scroll_restoration_basic_rendering(display: DisplayFixture):
    """Verify scroll_restoration renders its children inside a router."""

    @component
    def sample():
        return browser_router(
            route(
                "/",
                scroll_restoration(
                    link({"to": "/a", "id": "root-link"}, "Root"),
                    html.h1({"id": "home"}, "Home"),
                ),
            ),
            route(
                "/a",
                scroll_restoration(
                    link({"to": "/", "id": "back-link"}, "Back"),
                    html.h1({"id": "page-a"}, "Page A"),
                ),
            ),
        )

    await display.show(sample)
    await display.page.wait_for_selector("#home")
    assert await display.page.text_content("#home") == "Home"

    await display.page.click("#root-link")
    await display.page.wait_for_selector("#page-a")
    assert await display.page.text_content("#page-a") == "Page A"

    await display.page.click("#back-link")
    await display.page.wait_for_selector("#home")
    assert await display.page.text_content("#home") == "Home"


async def test_scroll_restoration_preserves_scroll(display: DisplayFixture):
    """Verify scroll position is preserved when navigating back."""

    @component
    def scroll_page():
        tall_content = [html.div({"style": {"height": "1500px"}}, f"Section {i}") for i in range(10)]
        link_list = link({"to": "/other", "id": "to-other"}, "Go to other", key="to-other")
        return scroll_restoration(
            html.h1({"id": "scroll-page"}, "Scroll Page"),
            *tall_content,
            link_list,
        )

    @component
    def other_page():
        return scroll_restoration(
            html.h1({"id": "other-page"}, "Other Page"),
            link({"to": "/", "id": "back-to-scroll"}, "Back to scroll page", key="back-to-scroll"),
        )

    @component
    def sample():
        return browser_router(
            route("/", scroll_page()),
            route("/other", other_page()),
        )

    await display.show(sample)

    # Wait for the scroll page to render
    await display.page.wait_for_selector("#scroll-page")

    # Scroll down 500px
    await display.page.evaluate("window.scrollTo(0, 500)")
    scroll_y = await display.page.evaluate("window.scrollY")
    assert scroll_y >= 500, f"Expected scrollY >= 500, got {scroll_y}"

    # Navigate to /other via link
    await display.page.click("#to-other")
    await display.page.wait_for_selector("#other-page")

    # Navigate back to / via link
    await display.page.click("#back-to-scroll")
    await display.page.wait_for_selector("#scroll-page")

    # Poll for scroll restoration to apply (it runs in useLayoutEffect which
    # fires synchronously after DOM commit, but the browser needs at least one
    # frame to paint when scrollTo is called during the same commit).
    await display.page.wait_for_function(
        "window.scrollY >= 450",
        timeout=5000,
    )
