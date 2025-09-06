import requests
import time
import asyncio
from playwright.async_api import async_playwright

async def run_playwright(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        start_time = time.time()
        response = await page.goto(url, timeout=20000)
        latency = time.time() - start_time
        status = response.status if response else "Unknown"
        charset = await page.evaluate("document.characterSet")
        content = await page.content()
        await browser.close()
        return {"status": status, "latency": latency, "charset": charset, "content": content}

def test_url(url: str, render: bool = False):
    if render:
        try:
            return asyncio.run(run_playwright(url))
        except Exception as e:
            return {"error": str(e)}
    else:
        try:
            start_time = time.time()
            response = requests.get(url, timeout=20)
            latency = time.time() - start_time
            response.raise_for_status()
            return {
                "status": response.status_code,
                "latency": latency,
                "charset": response.encoding,
                "content": response.text,
            }
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}