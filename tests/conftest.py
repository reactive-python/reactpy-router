import asyncio
import sys

import pytest
from playwright.async_api import async_playwright
from reactpy.testing import BackendFixture, DisplayFixture


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--headless",
        dest="headless",
        action="store_false",
        help="Hide the browser window when running web-based tests",
    )


@pytest.fixture
async def display(backend, browser):
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    async with DisplayFixture(backend, browser) as display_fixture:
        display_fixture.page.set_default_timeout(10000)
        yield display_fixture


@pytest.fixture
async def backend():
    async with BackendFixture() as backend_fixture:
        yield backend_fixture


@pytest.fixture
async def browser(pytestconfig):
    async with async_playwright() as pw:
        yield await pw.chromium.launch(headless=False)
