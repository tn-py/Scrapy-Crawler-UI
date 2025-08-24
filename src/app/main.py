import typer
from typing_extensions import Annotated
from parsel import Selector
from urllib.parse import urlparse
import os
import subprocess
from typing import List
from app.core import test_url

app = typer.Typer()

url_app = typer.Typer()
app.add_typer(url_app, name="url")

selector_app = typer.Typer()
app.add_typer(selector_app, name="selector")

spider_app = typer.Typer()
app.add_typer(spider_app, name="spider")

crawl_app = typer.Typer()
app.add_typer(crawl_app, name="crawl")

@url_app.command("test")
def url_test_command(url: str, render: Annotated[bool, typer.Option(help="Render javascript on the page.")] = False):
    """
    Test a single URL.
    """
    typer.echo(f"Testing {url}")
    result = test_url(url, render)
    if "error" in result:
        typer.echo(f"Error: {result['error']}", err=True)
    else:
        typer.echo(f"Status: {result['status']}")
        typer.echo(f"Latency: {result['latency']:.2f} seconds")
        typer.echo(f"Charset: {result['charset']}")

@selector_app.command("test")
def selector_test(
    url: str,
    selector: str,
    render: Annotated[bool, typer.Option(help="Render javascript on the page.")] = False,
):
    """
    Test a CSS selector on a URL.
    """
    typer.echo(f"Testing selector '{selector}' on {url}")
    content = ""
    if render:
        typer.echo("JS rendering enabled")
        try:
            _, _, _, content = test_url(url, render=True)
        except Exception as e:
            typer.echo(f"Error during rendering: {e}", err=True)
            return
    else:
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            content = response.text
        except requests.exceptions.RequestException as e:
            typer.echo(f"Error: {e}", err=True)
            return

    if content:
        sel = Selector(text=content)
        matches = sel.css(selector)
        typer.echo(f"Match count: {len(matches)}")
        if matches:
            typer.echo("First 3 text samples:")
            for match in matches[:3]:
                typer.echo(f"- {match.get().strip()}")
            typer.echo("First match outer HTML:")
            typer.echo(matches[0].get())

@selector_app.command("explain")
def selector_explain(selector: str):
    """
    Explain a CSS selector.
    """
    explanation = explain_selector(selector)
    typer.echo(explanation)

@selector_app.command("repair")
def selector_repair(url: str, selector: str):
    """
    Repair a broken CSS selector.
    """
    repair_suggestion = repair_selector(url, selector)
    typer.echo(repair_suggestion)

@spider_app.command("scaffold")
def spider_scaffold(
    name: str,
    url: str,
    selector: str,
):
    """
    Scaffold a new spider.
    """
    typer.echo(f"Scaffolding spider: {name}")

    # Get base path
    base_path = os.getcwd()

    # Generate spider code
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

    # Generate item code
    item_code = f"""
import scrapy

class {item_class_name}(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
"""

    # Write spider file
    spider_file_path = os.path.join(base_path, "src", "project", "spiders", f"{name}.py")
    with open(spider_file_path, "w") as f:
        f.write(spider_code)
    typer.echo(f"Created spider: {spider_file_path}")

    # Write item file
    item_file_path = os.path.join(base_path, "src", "project", "items.py")
    with open(item_file_path, "a") as f:
        f.write("\n\n" + item_code)
    typer.echo(f"Updated items: {item_file_path}")

@crawl_app.command("run")
def crawl_run(
    spider: str,
    arg: Annotated[List[str], typer.Option("--arg", help="Spider arguments.")] = None,
    out: Annotated[str, typer.Option("--out", help="Output file.")] = None,
):
    """
    Run a spider.
    """
    typer.echo(f"Running spider: {spider}")
    
    command = ["scrapy", "crawl", spider]
    if arg:
        for a in arg:
            command.extend(["-a", a])
    if out:
        command.extend(["-O", out])

    command_str = " ".join(command)
    typer.echo(f"Executing command: {command_str}")
    
    process = subprocess.run(command, capture_output=True, text=True)
    typer.echo(process.stdout)
    typer.echo(process.stderr, err=True)


if __name__ == "__main__":
    app()
