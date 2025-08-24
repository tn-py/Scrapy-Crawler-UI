# Scrape-Scripts: Scalable Web Scraping System

## Project Overview

Scrape-Scripts is a fast, scalable Python system designed for web scraping, built with Scrapy, a FastAPI backend, and a React frontend. It provides tools for testing URL reachability, validating CSS selectors, generating reusable spiders, executing crawls at scale, and exporting normalized CSV files. All components are containerized for easy deployment on Coolify via Docker.

## Tech Stack

*   **Backend & CLI**: Python 3.12 (FastAPI, Scrapy, Typer)
*   **Frontend**: React with Bootstrap CSS
*   **Containerization**: Docker
*   **Deployment**: Coolify
*   **Tooling**: ruff, black, mypy (strict), pytest (coverage ≥ 90%)
*   **Web Scraping**: Scrapy, Parsel (for selectors), Pydantic (for item validation)
*   **Optional JS Rendering**: `scrapy-playwright`
*   **Optional Orchestration**: Scrapyd

## Architecture

The application follows a clear separation of concerns:

*   **Frontend (src/ui)**: A React application with Bootstrap CSS that provides a user-friendly web interface for all scraper operations. This is where users will interact with the system to initiate crawls, test selectors, and manage spiders.

*   **Backend (src/api)**: A FastAPI application that exposes a REST API to the frontend. This API acts as a wrapper around the core Scrapy and Typer logic, allowing the frontend to communicate with and control the scraping processes.

*   **Scraper (src/project)**: The core web scraping component built with Scrapy. It includes:
    *   **Spiders**: Responsible for acquiring data from websites.
    *   **Items**: Define the schema for the scraped data, validated with Pydantic.
    *   **Pipelines**: Process scraped items for validation, normalization, and storage.
    *   **Middlewares**: Handle various aspects like retries, custom headers, caching, and optional JavaScript rendering (`scrapy-playwright`).
    *   **Settings**: Centralized configuration for Scrapy, with environment variable overrides.

*   **CLI Wrappers (src/app)**: Typer-based command-line interface (CLI) tools for direct interaction, including URL/selector tests and job manifests.

*   **Selector Tools (src/selector_tools)**: Provides helpers for explaining and repairing CSS selectors, including suggestions for fixes when no matches are found.

## How to Run the Application

The application is designed for containerized deployment using Docker and Coolify.

1.  **Prerequisites**:
    *   Docker installed and running.
    *   Coolify instance (or similar Docker orchestration platform) for deployment.

2.  **Build Docker Images**:
    Navigate to the project root and build the Docker images. (Specific commands will depend on the `Dockerfile` and `docker-compose.yml` in `infra/`). A typical command might look like:
    ```bash
    docker-compose -f infra/docker-compose.yml build
    ```

3.  **Run Containers**:
    Once built, you can run the containers. For development, you might use:
    ```bash
    docker-compose -f infra/docker-compose.yml up
    ```
    For production deployment on Coolify, you would configure your Coolify instance to pull and deploy these Docker images.

4.  **Access the Application**:
    *   **Frontend**: The React UI will typically be accessible via a web browser at a specified port (e.g., `http://localhost:3000` or the URL provided by Coolify).
    *   **Backend API**: The FastAPI backend will expose its API endpoints (e.g., `http://localhost:8000` or the URL provided by Coolify).

## CLI Commands

The application provides a set of command-line interface (CLI) tools for scripting and automation, accessible via the `agent` command:

*   **`agent url test <URL> [--render]`**
    *   **Purpose**: Reports the status, latency, and character set of a given URL.
    *   **Example**: `agent url test https://example.com`

*   **`agent selector test <URL> --selector ".price" [--render]`**
    *   **Purpose**: Tests a CSS selector against a live page. Reports the match count, the first three text samples, and the outer HTML of the first match.
    *   **Example**: `agent selector test https://example.com --selector "h1.title"`

*   **`agent spider scaffold <NAME> --url <URL> --selector ".item"`**
    *   **Purpose**: Generates a base Scrapy spider, an item definition, and associated tests, pre-wired to export data via Scrapy FEEDS.
    *   **Example**: `agent spider scaffold MyNewSpider --url https://example.com/products --selector ".product-card"`

*   **`agent crawl run <SPIDER> [--arg k=v ...] [--out /data/out/custom.csv]`**
    *   **Purpose**: Executes a Scrapy crawl for a specified spider. Allows passing additional arguments to the spider and overriding the output CSV file path.
    *   **Example**: `agent crawl run MyNewSpider --arg category=electronics --out /data/out/electronics_crawl.csv`

## Repository Layout

```
pyproject.toml
scrapy.cfg
src
  api                  # FastAPI backend application
  app                  # Typer CLI wrappers (URL/selector tests, job manifests)
  project              # Scrapy package
    items.py
    pipelines.py
    middlewares.py
    settings.py
    spiders
  selector_tools       # explain/repair helpers
  ui                   # React frontend application
tests
infra
  Dockerfile
  docker-compose.yml   # optional: scrapyd + app
  prometheus.yml       # optional
GEMINI.md
README.md
```

## Scrapy Baseline Settings

The project adheres to the following baseline Scrapy settings for politeness, speed, and compliance:

*   `BOT_NAME`: Set to a clear product name.
*   `USER_AGENT`: Transparent identifier with contact information.
*   `CONCURRENT_REQUESTS = 32`
*   `CONCURRENT_REQUESTS_PER_DOMAIN = 8` (tune per target)
*   `DOWNLOAD_TIMEOUT ≈ 20s`
*   Retries enabled (~2 additional tries for connect/server errors).
*   AutoThrottle enabled (`start ~0.5s`, `max ~10s`, `target concurrency ~4`).
*   HTTP cache enabled in development; disabled in production unless deterministic replay is required.
*   FEEDS configured to write CSVs to `file:///data/out` using `%(name)s` and `%(time)s` placeholders and a fixed field list.

## Testing Strategy

*   **Spider Contracts**: Quick callback verification on sample URLs using docstring directives (`@url`, `@returns`, `@scrapes`).
*   **Unit Tests**: For selector tools, pipelines, and custom middlewares.
*   **Golden-File Tests**: With static HTML fixtures for determinism.
*   **Coverage**: ≥ 90%.

## Security and Compliance

*   Secrets loaded from environment variables only.
*   No logging of credentials or personal data.
*   Respects site terms and `robots.txt`.
*   Default to a transparent `User-Agent`; randomized rotation is opt-in.
*   Does not bypass paywalls or abuse rate limits.

---
