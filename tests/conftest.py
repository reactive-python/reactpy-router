import asyncio
import os
import sys

import pytest
from playwright.async_api import async_playwright
from reactpy.testing import BackendFixture, DisplayFixture

GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS", "").lower() == "true"


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--headless",
        dest="headless",
        action="store_true",
        help="Hide the browser window when running web-based tests",
    )


@pytest.fixture
async def display(backend, browser):
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
        yield await pw.chromium.launch(headless=True if GITHUB_ACTIONS else pytestconfig.getoption("headless"))


@pytest.fixture
def event_loop_policy(request):
    if sys.platform == "win32":
        return asyncio.WindowsProactorEventLoopPolicy()
    return asyncio.get_event_loop_policy()
