from playwright.async_api._generated import Page


async def page_load_complete(page: Page) -> None:
    """Only return when network is idle and DOM has loaded"""
    await page.wait_for_load_state("networkidle")
    await page.wait_for_load_state("domcontentloaded")
