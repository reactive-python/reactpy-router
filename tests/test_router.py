import asyncio
import os
from typing import Any

import pytest
from playwright.async_api._generated import Browser, Page
from reactpy import Ref, component, html, use_location, use_state
from reactpy.testing import DisplayFixture

from reactpy_router import browser_router, link, navigate, route, use_params, use_search_params

GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS", "").lower() == "true"
CLICK_DELAY = 250 if GITHUB_ACTIONS else 25  # Delay in miliseconds.
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

    try:
        root_element = await display.root_element()
    except AttributeError:
        root_element = await display.page.wait_for_selector(
            f"#display-{display._next_view_id}",  # type: ignore
            state="attached",
        )

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
        _link = await display.page.wait_for_selector(link_selector)
        await _link.click(delay=CLICK_DELAY)

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
        _link = await display.page.wait_for_selector(link_selector)
        await _link.click(delay=CLICK_DELAY)

    await display.page.wait_for_selector("#default")

    link_selectors.reverse()
    for link_selector in link_selectors:
        await asyncio.sleep(CLICK_DELAY / 1000)
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
        _link = await display.page.wait_for_selector(link_selector)
        await _link.click(delay=CLICK_DELAY)

    await display.page.wait_for_selector("#default")

    selectors.reverse()
    for link_selector in selectors:
        await asyncio.sleep(CLICK_DELAY / 1000)
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
    _link = await display.page.wait_for_selector("#root")
    await _link.click(delay=CLICK_DELAY)
    await display.page.wait_for_selector("#success")


async def test_link_class_name(display: DisplayFixture):
    @component
    def sample():
        return browser_router(route("/", link({"to": "/a", "id": "root", "className": "class1"}, "Root")))

    await display.show(sample)

    _link = await display.page.wait_for_selector("#root")
    assert "class1" in await _link.get_attribute("class")


async def test_link_href(display: DisplayFixture):
    @component
    def sample():
        return browser_router(route("/", link({"href": "/a", "id": "root"}, "Root")))

    await display.show(sample)

    _link = await display.page.wait_for_selector("#root")
    assert "/a" in await _link.get_attribute("href")


async def test_ctrl_click(display: DisplayFixture, browser: Browser):
    @component
    def sample():
        return browser_router(
            route("/", link({"to": "/a", "id": "root"}, "Root")),
            route("/a", link({"to": "/a", "id": "a"}, "a")),
        )

    await display.show(sample)

    _link = await display.page.wait_for_selector("#root")
    await _link.click(delay=CLICK_DELAY, modifiers=["Control"])
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
    _button = await display.page.wait_for_selector("button")
    await _button.click(delay=CLICK_DELAY)
    await display.page.wait_for_selector("#a")
    await asyncio.sleep(CLICK_DELAY / 1000)
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
    _button = await display.page.wait_for_selector("#nav-a")
    await _button.click(delay=CLICK_DELAY)
    _button = await display.page.wait_for_selector("#nav-b")
    await _button.click(delay=CLICK_DELAY)
    await display.page.wait_for_selector("#b")
    await asyncio.sleep(CLICK_DELAY / 1000)
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
    _button = await display.page.wait_for_selector("#root-a")
    await _button.click(delay=CLICK_DELAY)
    _button = await display.page.wait_for_selector("#nav-a")
    await _button.click(delay=CLICK_DELAY)
    await asyncio.sleep(CLICK_DELAY / 1000)
    await display.page.wait_for_selector("#nav-a")
    await asyncio.sleep(CLICK_DELAY / 1000)
    await display.page.go_back()
    await display.page.wait_for_selector("#root-a")
