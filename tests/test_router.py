import pytest
from idom import Ref, component, html
from idom.testing import BackendFixture, DisplayFixture

from idom_router import Link, Route, configure


@pytest.fixture
def Routes(backend: BackendFixture):
    return configure(backend.implementation)


async def test_simple_router(display: DisplayFixture, Routes: Routes):
    @component
    def Sample():
        return Routes(
            Route("/a", html.h1({"id": "a"}, "A")),
            Route("/b", html.h1({"id": "b"}, "B")),
            Route("/c", html.h1({"id": "c"}, "C")),
            Route("/c", html.h1({"id": "c"}, "C")),
            Route("/*", html.h1({"id": "default"}, "Default")),
        )

    await display.show(Sample)

    for path, selector in [
        ("/a", "#a"),
        ("/b", "#b"),
        ("/c", "#c"),
        ("/default", "#default"),
        ("/anything", "#default"),
    ]:
        await display.goto(path)
        await display.page.wait_for_selector(selector)


async def test_navigate_with_link(display: DisplayFixture, Routes: Routes):
    render_count = Ref(0)

    @component
    def Sample():
        render_count.current += 1
        return Routes(
            Route("/", Link({"id": "root"}, "Root", to="/a")),
            Route("/a", Link({"id": "a"}, "A", to="/b")),
            Route("/b", Link({"id": "b"}, "B", to="/c")),
            Route("/c", Link({"id": "c"}, "C", to="/default")),
            Route("/*", html.h1({"id": "default"}, "Default")),
        )

    await display.show(Sample)

    for link_selector in ["#root", "#a", "#b", "#c"]:
        link = await display.page.wait_for_selector(link_selector)
        await link.click()

    await display.page.wait_for_selector("#default")

    # check that we haven't re-rendered the root component by clicking the link
    # (i.e. we are preventing default link behavior)
    assert render_count.current == 1
