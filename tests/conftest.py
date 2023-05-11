import pytest
from playwright.async_api import async_playwright
from reactpy.testing import BackendFixture, DisplayFixture


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--headed",
        dest="headed",
        action="store_true",
        help="Open a browser window when runnging web-based tests",
    )


@pytest.fixture
async def display(backend, browser):
    async with DisplayFixture(backend, browser) as display:
        display.page.set_default_timeout(10000)
        yield display


@pytest.fixture
async def backend():
    async with BackendFixture() as backend:
        yield backend


@pytest.fixture
async def browser(pytestconfig):
    async with async_playwright() as pw:
        yield await pw.chromium.launch(headless=not bool(pytestconfig.option.headed))
