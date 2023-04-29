from idom import Ref, component, html, use_location
from idom.testing import DisplayFixture

from idom_router import Route, link, router, use_params, use_query
from tests.utils import compile_simple_regex_route


async def test_simple_router(display: DisplayFixture):
    def make_location_check(path, *routes):
        name = path.lstrip("/").replace("/", "-")

        @component
        def check_location():
            assert use_location().pathname == path
            return html.h1({"id": name}, path)

        return Route(path, check_location(), *routes)

    @component
    def sample():
        return router(
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
            f"#display-{display._next_view_id}", state="attached"
        )

    assert not await root_element.inner_html()


async def test_nested_routes(display: DisplayFixture):
    @component
    def sample():
        return router(
            Route(
                "/a",
                html.h1({"id": "a"}, "A"),
                Route(
                    "/b",
                    html.h1({"id": "b"}, "B"),
                    Route("/c", html.h1({"id": "c"}, "C")),
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
        return router(
            Route("/", link("Root", to="/a", id="root")),
            Route("/a", link("A", to="/b", id="a")),
            Route("/b", link("B", to="/c", id="b")),
            Route("/c", link("C", to="/default", id="c")),
            Route("/{path:path}", html.h1({"id": "default"}, "Default")),
        )

    await display.show(sample)

    for link_selector in ["#root", "#a", "#b", "#c"]:
        lnk = await display.page.wait_for_selector(link_selector)
        await lnk.click()

    await display.page.wait_for_selector("#default")

    # check that we haven't re-rendered the root component by clicking the link
    # (i.e. we are preventing default link behavior)
    assert render_count.current == 1


async def test_use_params(display: DisplayFixture):
    expected_params = {}

    @component
    def check_params():
        assert use_params() == expected_params
        return html.h1({"id": "success"}, "success")

    @component
    def sample():
        return router(
            Route(
                "/first/{first:str}",
                check_params(),
                Route(
                    "/second/{second:str}",
                    check_params(),
                    Route(
                        "/third/{third:str}",
                        check_params(),
                    ),
                ),
            )
        )

    await display.show(sample)

    for path, expected_params in [
        ("/first/1", {"first": "1"}),
        ("/first/1/second/2", {"first": "1", "second": "2"}),
        ("/first/1/second/2/third/3", {"first": "1", "second": "2", "third": "3"}),
    ]:
        await display.goto(path)
        await display.page.wait_for_selector("#success")


async def test_use_query(display: DisplayFixture):
    expected_query = {}

    @component
    def check_query():
        assert use_query() == expected_query
        return html.h1({"id": "success"}, "success")

    @component
    def sample():
        return router(Route("/", check_query()))

    await display.show(sample)

    expected_query = {"hello": ["world"], "thing": ["1", "2"]}
    await display.goto("?hello=world&thing=1&thing=2")
    await display.page.wait_for_selector("#success")


async def test_custom_path_compiler(display: DisplayFixture):
    expected_params = {}

    @component
    def check_params():
        assert use_params() == expected_params
        return html.h1({"id": "success"}, "success")

    @component
    def sample():
        return router(
            Route(
                r"/first/(?P<first__int>\d+)",
                check_params(),
                Route(
                    r"/second/(?P<second__float>[\d\.]+)",
                    check_params(),
                    Route(
                        r"/third/(?P<third__list>[\d,]+)",
                        check_params(),
                    ),
                ),
            ),
            compiler=compile_simple_regex_route,
        )

    await display.show(sample)

    for path, expected_params in [
        ("/first/1", {"first": 1}),
        ("/first/1/second/2.1", {"first": 1, "second": 2.1}),
        (
            "/first/1/second/2.1/third/3,3",
            {"first": 1, "second": 2.1, "third": ["3", "3"]},
        ),
    ]:
        await display.goto(path)
        await display.page.wait_for_selector("#success")
