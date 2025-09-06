from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import test_url
from parsel import Selector
from selector_tools.main import explain_selector, repair_selector
from urllib.parse import urlparse
import subprocess
import os

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/url/test")
def test_url_endpoint(url: str, render: bool = False):
    return test_url(url, render)

@app.get("/selector/test")
def selector_test_endpoint(url: str, selector: str, render: bool = False):
    result = test_url(url, render)

    if "error" in result:
        return {"error": result["error"]}

    content = result.get("content", "")
    if content:
        sel = Selector(text=content)
        matches = sel.css(selector)
        return {"match_count": len(matches)}
    return {"match_count": 0}

@app.get("/selector/explain")
def selector_explain_endpoint(selector: str):
    return {"explanation": explain_selector(selector)}

@app.get("/selector/repair")
def selector_repair_endpoint(url: str, selector: str):
    return {"suggestion": repair_selector(url, selector)}

@app.get("/selector/discover")
def selector_discover_endpoint(url: str):
    try:
        result = test_url(url, False)
        content = result.get("content", "")
        if not content:
            return {"error": result.get("error", "Could not fetch content")}

        sel = Selector(text=content)
        discovered = []
        for element in sel.css('*:not(script):not(style):not(head)'):
            text = element.xpath('string(.)').get().strip()
            if text:
                tag = element.root.tag
                classes = element.attrib.get('class', '').split()
                if classes:
                    class_selector = '.' + '.'.join(classes)
                    selector = f"{tag}{class_selector}"
                    if len(sel.css(selector)) == 1 and selector not in [d['selector'] for d in discovered]:
                        discovered.append({'selector': selector, 'data': text[:100]})
            if len(discovered) >= 50:
                break
        return {"selectors": discovered}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


@app.get("/spider/scaffold")
def spider_scaffold_endpoint(name: str, url: str, selector: str):
    spider_class_name = f"{name.capitalize()}Spider"
    item_class_name = f"{name.capitalize()}Item"
    allowed_domain = urlparse(url).netloc
    spider_code = f"""
import scrapy
from project.items import {item_class_name}

class {spider_class_name}(scrapy.Spider):
    name = "{name}"
    allowed_domains = ["{allowed_domain}"]
    start_urls = ["{url}"]

    def parse(self, response):
        for item in response.css("{selector}"):
            yield {item_class_name}()
"""

    item_code = f"""
import scrapy

class {item_class_name}(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
"""

    return {"spider_code": spider_code, "item_code": item_code}

@app.post("/crawl/run")
def crawl_run_endpoint(spider: str, arg: list[str] = [], out: str = None):
    # Security check: ensure the spider name is valid and doesn't contain any malicious characters
    if not spider.isalnum():
        return {"error": "Invalid spider name"}

    # Security check: ensure the spider file exists
    spider_path = os.path.join("src", "project", "spiders", f"{spider}.py")
    if not os.path.exists(spider_path):
        return {"error": f"Spider not found: {spider}"}

    command = ["scrapy", "crawl", spider]
    if arg:
        for a in arg:
            command.extend(["-a", a])
    if out:
        command.extend(["-O", out])

    process = subprocess.run(command, capture_output=True, text=True)
    return {"stdout": process.stdout, "stderr": process.stderr}