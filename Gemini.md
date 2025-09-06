# GEMINI.md — Project Rules (Scrapy Edition)

## Mission & Scope

You are the project’s AI engineer. Build a **fast, scalable** Python system using **Scrapy** to (a) test URL reachability, (b) validate **CSS selectors** against live pages, (c) generate reusable **spiders/extractors**, (d) execute crawls at scale, and (e) **export** normalized CSVs. All deliverables must be **containerized** and deploy‑ready on **Coolify** via Docker.

> Scrapy provides first‑class CSS/XPath selector tooling via **Parsel**; use it for selector tests and extraction. citeturn0search0turn0search5

## Non‑Negotiables

* **Runtime**: Python **3.12**. Tooling: `ruff` + `black`, `mypy --strict`, `pytest` (coverage ≥ 90%).
* **Framework**: **Scrapy 2.13+** for crawling; selectors via **Parsel**; item validation with `pydantic`.
* **JS‑heavy pages**: Prefer HTML‑only; when not possible, enable **scrapy‑playwright** as a download handler (Chromium headless, pooled contexts). Keep it opt‑in via settings/env. citeturn0search1turn0search21
* **Exports**: Use Scrapy **FEEDS** to write CSV to `/data/out/%(name)s_%(time)s.csv` with a **stable column order**. Use built‑in storage URI parameters `%(name)s` and `%(time)s`. citeturn2search0turn2search1
* **Politeness & speed**: Enable **AutoThrottle**; set bounded concurrency, per‑domain limits, backoff/jitter. Defaults are conservative; tune per job. citeturn0search4
* **Ops**: Deterministic builds (locked deps), healthcheck endpoint, non‑root user, and read‑only FS where viable.
* **Compliance**: Respect `robots.txt`, explicit `User‑Agent`, and site ToS. No paywall bypasses or abuse.

## Guardrails for the Agent (How You Work)

* **Plan → Diff → Apply → Test → Run** on every change.
* Generate **code + tests + README deltas** together. Never modify outside `/src` and `/infra`.
* Prefer *small, reversible* patches with conventional commits.

## Architecture North Star

* **Project type**: Scrapy project with clean boundaries: spiders (data acquisition), items (schema), pipelines (validation/normalization), middlewares (retries, headers, caching), and settings.
* **Selector intelligence**: Provide a selector “explain/repair” helper using Parsel + lightweight heuristics to suggest fixes when matches are zero.
* **Scale**: Concurrency via Scrapy settings; optional persistent scheduling via **Scrapyd** for remote orchestration (Coolify‑hosted). citeturn0search2

## Target Repo Layout

```
/pyproject.toml
/scrapy.cfg
/src
  /app                 # thin Typer CLI wrappers (url/selector tests, job manifests)
  /project             # Scrapy project package
    /items.py          # pydantic Item definitions + adapters
    /pipelines.py      # validation/normalization → CSV fields_json, etc.
    /middlewares.py    # UA, retries, cookies, cache, playwright toggles
    /settings.py       # single source of truth (overridable via env)
    /spiders           # generated & manual spiders
  /selector_tools      # explain/repair CSS selectors (Parsel)
/tests
/infra
  Dockerfile
  docker-compose.yml   # optional scrapyd + app service for orchestration
  prometheus.yml       # optional metrics exporter via Scrapy stats bridge
/GEMINI.md             # this file
/README.md
```

## CLI Surface (Typer wrappers)

* `agent url test URL [--render]` → one‑off HEAD/GET via Scrapy downloader; log status, latency, robots stance.
* `agent selector test URL --selector ".price" [--render]` → fetch page once, run Parsel CSS; print count + first 3 texts + first match outerHTML.
* `agent spider scaffold NAME --url URL --selector ".item"` → generate base spider + item + test (contracts) wired to FEEDS.
* `agent crawl run SPIDER [--arg k=v ...] [--out /data/out/custom.csv]` → executes `scrapy crawl` with FEEDS override.

## Data Contracts (CSV)

Strict order:

```
source_url,status,fetched_at_iso,selector,match_count,sample_text,sample_html,fields_json
```

* `fields_json` carries key/value payloads extracted by items/pipelines.
* UTF‑8, RFC4180 quoting, newline at EOF.

## Scrapy Settings (baseline)

Place in `/src/project/settings.py`; allow env overrides.

```python
BOT_NAME = "selector_sage"
SPIDER_MODULES = ["project.spiders"]
NEWSPIDER_MODULE = "project.spiders"
ROBOTSTXT_OBEY = True
USER_AGENT = "ELU-SelectorSage/1.0 (+contact@email; purpose=research)"
# Concurrency & throttling
CONCURRENT_REQUESTS = 32
CONCURRENT_REQUESTS_PER_DOMAIN = 8
DOWNLOAD_TIMEOUT = 20
RETRY_ENABLED = True
RETRY_TIMES = 2
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0
# HTTP cache (dev/local) to reduce load during iteration
HTTPCACHE_ENABLED = True
HTTPCACHE_IGNORE_HTTP_CODES = [301, 302]
# FEEDS → dynamic file name per spider & run
FEEDS = {
  "file:///data/out/%(name)s_%(time)s.csv": {
    "format": "csv",
    "fields": [
      "source_url","status","fetched_at_iso","selector",
      "match_count","sample_text","sample_html","fields_json"
    ],
    "overwrite": True,
  }
}
```

> AutoThrottle dynamically adjusts rate based on load; FEEDS handles CSV serialization and supports `%(name)s`/`%(time)s` placeholders for file names. citeturn0search4turn2search1

### Optional: JS Rendering via scrapy‑playwright

Enable only when necessary:

```python
# settings.py
DOWNLOAD_HANDLERS = {"http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                     "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"}
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 20000
```

Usage in a spider:

```python
yield Request(url, meta={"playwright": True})
```

> The plugin integrates Playwright without breaking Scrapy’s scheduling or item pipeline model. citeturn0search1

### Optional: Remote Orchestration via Scrapyd

Expose a Scrapyd service to **schedule/list** jobs from the API (Coolify can host both app and Scrapyd in the same stack). Keep job storage persistent. citeturn0search2

## Testing Strategy

* **Spider contracts** for callback sanity on sample URLs (docstring `@url`, `@returns`, `@scrapes`).
* Unit tests for selector tools, pipelines, and any custom middlewares.
* Golden‑file tests for generated spiders (static HTML fixtures for deterministic runs).

> Spider **contracts** are a built‑in way to test Scrapy callbacks quickly. citeturn1search0

## Observability

* Structured JSON logs (request\_id, url, selector, duration\_ms, status, retries).
* Bridge Scrapy **stats** to Prometheus via a tiny exporter or existing extension; record RED metrics.

## Script/Spider Generation Rules

* Generator emits:

  * `spiders/NAME.py` with typed `Item` and clear `parse_*` callbacks
  * `tests/test_NAME_contracts.py` (contracts) + HTML fixture
  * Registration in README with usage examples
* Spider docstring must state: purpose, selectors used, failure modes, and sample output.

## Concurrency & Resilience Playbook

* Tune `CONCURRENT_REQUESTS`, per‑domain caps, and AutoThrottle ceilings per target.
* Enable HTTP cache during development to reduce re‑fetches; disable in prod unless you need deterministic replay. citeturn1search2
* Circuit‑breaker semantics can be implemented in middleware (track host error streaks; short‑circuit for a cooldown window).

## Security & Compliance

* Secrets only via env (no hard‑coding). Scrub PII from logs. Respect robots/ToS.

## Docker & Coolify (reference)

* **Multi‑stage** build; ship only wheels + app. Run as a non‑root user; expose port `8000` if you add a minimal FastAPI/healthcheck layer.
* Preinstall Playwright browsers only if `scrapy‑playwright` is enabled to avoid cold‑start downloads.

### Example Dockerfile (Scrapy + optional Playwright)

```dockerfile
# ---- builder ----
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder
WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project
COPY . .
RUN uv build

# ---- runtime ----
FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
# system deps for lxml/OpenSSL/Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates libxml2 libxslt1.1 libffi8 libnss3 \
    && rm -rf /var/lib/apt/lists/*
# (optional) playwright browsers – comment out if not using scrapy-playwright
# RUN pip install playwright && playwright install --with-deps chromium
RUN useradd -u 10001 -m app
WORKDIR /app
COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl
RUN mkdir -p /data/out && chown -R app:app /data
USER app
# healthcheck if you add a tiny FastAPI on :8000
# HEALTHCHECK CMD curl -f http://localhost:8000/healthz || exit 1
CMD ["bash", "-lc", "scrapy list && sleep infinity"]
```

## Operational Playbook (Agent)

1. **When asked to add a spider**: plan → scaffold spider + item + contracts → run contracts → run a small live crawl → attach CSV sample + metrics.
2. **When asked to test a selector**: fetch once → report count + 3 text samples + first outerHTML + fragility score → offer a repair hint.
3. **When asked to run at scale**: surface a tuned settings diff (concurrency, throttling, retries) + monitoring plan (stats, Prometheus, logs).

---

### Quickstart Tasks (for Gemini)

* Initialize Scrapy project, baseline `settings.py`, and Typer CLI wrappers.
* Implement `selector_tools.explain/repair`.
* Implement `pipelines.py` to normalize and serialize to CSV columns above.
* Add Dockerfile + (optional) Scrapyd compose file.

**Primary references**: Scrapy selectors/Parsel, FEEDS/CSV exports, AutoThrottle, scrapy‑playwright integration, and Scrapyd API. citeturn0search0turn2search0turn0search4turn0search1turn0search2
