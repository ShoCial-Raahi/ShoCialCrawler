import asyncio
from crawl4ai import AsyncWebCrawler

class Fetcher:
    @staticmethod
    async def fetch_page(url: str):
        # headless=True is default, but ensuring it's explicit. 
        # If user wants to see browser, set headless=False
        async with AsyncWebCrawler(verbose=True, headless=True) as crawler:
            # Scroll to bottom script
            js_code = "window.scrollTo(0, document.body.scrollHeight);"
            result = await crawler.arun(url=url, magic=True, js_code=js_code, wait_for="body")
            return result.html
