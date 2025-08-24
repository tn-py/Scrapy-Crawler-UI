# GEMINI.md — Project Rules (Scrapy Edition)

## 1. Mission and Scope

You are the project’s AI engineer. Build a fast, scalable Python system using **Scrapy**, with a **FastAPI** backend and a **React** frontend to:

* Test URL reachability
* Validate CSS selectors against live pages
* Generate reusable spiders and extractors
* Execute crawls at scale
* Export normalized CSV files

All deliverables must be containerized and deployable on **Coolify** via **Docker**.

## 2. Non-Negotiables

* **Runtime:** Python 3.12
  **Tooling:** ruff, black, mypy (strict), pytest (coverage ≥ 90%).
* **Framework:** Scrapy (current stable), selectors via Parsel, item validation with Pydantic.
* **JS-heavy pages:** Only when required; enable `scrapy-playwright` as an optional download handler.
* **Exports:** Use Scrapy FEEDS to write CSV to `/data/out` with a stable column order and dynamic filename using spider name and time.
* **Politeness and speed:** Enable AutoThrottle; use bounded concurrency, per-domain caps, and retry with backoff and jitter.
* **Operations:** Deterministic builds with locked dependencies; container healthcheck; non-root user; read-only filesystem where feasible.
* **Compliance:** Set an explicit `User-Agent`, respect site terms; do not bypass paywalls or abuse rate limits.

## 3. Agent Guardrails

* Always follow: **Plan → Diff → Apply → Test → Run**.
* Produce code, tests, and README deltas together.
* Keep changes small and reversible; use conventional commits.
* Do not modify anything outside `/src` and `/infra`.

## 4. Architecture

* **Frontend:** A **React** application with Bootstrap CSS providing a user-friendly interface for all scraper operations.
* **Backend:** A **FastAPI** application that exposes a REST API to the frontend. This API will wrap the core Scrapy and Typer logic.
* **Scraper:** Standard Scrapy boundaries: spiders (acquisition), items (schema), pipelines (validation/normalization), middlewares (retries/headers/cache/rendering), settings (single source of truth with env overrides).
* Selector intelligence: provide an **explain** and **repair** helper for CSS selectors; suggest fixes when zero matches occur.
* Scale via Scrapy concurrency and throttling. Optional remote orchestration with **Scrapyd**.

## 5. Repository Layout

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

## 6. UI and CLI Surface

The application is primarily controlled through a React-based web interface. The following CLI commands are also available for scripting and automation:

* `agent url test <URL> [--render]`
  Reports status, latency, charset.
* `agent selector test <URL> --selector ".price" [--render]`
  Reports match count, first three text samples, first match outerHTML.
* `agent spider scaffold <NAME> --url <URL> --selector ".item"`
  Generates base spider, item, and test wired to FEEDS.
* `agent crawl run <SPIDER> [--arg k=v ...] [--out /data/out/custom.csv]`
  Executes `scrapy crawl` with FEEDS override.

## 7. Data Contracts for CSV

* **Columns (strict order):**
  `source_url, status, fetched_at_iso, selector, match_count, sample_text, sample_html, fields_json`
* `fields_json` contains a JSON string of extracted key–value pairs.
* UTF-8; RFC4180 quoting; newline at end of file.

## 8. Baseline Scrapy Settings (Descriptive)

* `BOT_NAME` set to a clear product name.

* `USER_AGENT` set to a transparent identifier with contact information.
* Start with `CONCURRENT_REQUESTS = 32`, `CONCURRENT_REQUESTS_PER_DOMAIN = 8`; tune per target.
* `DOWNLOAD_TIMEOUT ≈ 20s`.
* Retries enabled with \~2 additional tries for connect/server errors.
* AutoThrottle enabled (`start ~0.5s`, `max ~10s`, `target concurrency ~4`).
* HTTP cache enabled in development; disable in production unless deterministic replay is required.
* FEEDS configured to write CSVs to `file:///data/out` using `%(name)s` and `%(time)s` placeholders and a fixed field list.

## 9. Optional JS Rendering with `scrapy-playwright`

* Activate the download handler for `http` and `https` only when necessary.
* Keep Chromium headless and reuse contexts.
* Enable per request via `meta={"playwright": True}`.

## 10. Optional Remote Orchestration with Scrapyd

* Run Scrapyd in the same Coolify stack or a separate one.
* Persist job state to disk.
* Use the Scrapyd HTTP API to schedule, list, and cancel jobs.

## 11. Testing Strategy

* Spider contracts for quick callback verification on sample URLs (docstring directives for `@url`, `@returns`, `@scrapes`).
* Unit tests for selector tools, pipelines, and custom middlewares.
* Golden-file tests with static HTML fixtures for determinism.
* Coverage threshold ≥ 90%.

## 12. Observability

* Structured JSON logs (timestamp, level, event, url, selector, duration\_ms, status, retries).
* Bridge Scrapy stats to Prometheus using a lightweight exporter.
* Track request totals, latency histograms, zero-hit selectors, extractor failures.
* Emit a run summary with row counts and failure taxonomy.

## 13. Script and Spider Generation Rules

* Generator produces:

  * Spider module with typed Item, explicit `parse*` callbacks, and clear start requests.
  * Tests and an HTML fixture.
  * README section with usage and expected CSV columns.
* Spider docstring includes purpose, selectors used, failure modes, and sample output.

## 14. Concurrency and Resilience

* Tune global and per-domain concurrency for each target.
* Keep AutoThrottle enabled; adjust ceilings when hosts allow higher throughput.
* Implement a simple middleware circuit breaker (open after a configurable failure streak; cooldown before retry).
* Use HTTP cache selectively during development to avoid hot loops.

## 15. Security and Compliance

* Load secrets from environment variables only.
* Do not log credentials or personal data.
* Respect site terms.
* Default to a transparent `User-Agent`; randomized rotation is opt-in.

## 16. Docker and Coolify Guidance

* Multi-stage build that compiles dependencies and copies only wheels and the application into the runtime image.
* Non-root user with fixed UID.
* Optional healthcheck endpoint (e.g., via a lightweight FastAPI layer), or rely on container exit codes and logs.
* Preinstall Playwright browsers only if `scrapy-playwright` is enabled.
* Persist `/data` for outputs.
* Prefer read-only root filesystem; mount `tmpfs` for temporary files if required.

## 17. Operational Playbook

* **Add a spider:** plan, scaffold spider + item + contracts, run contracts, run a small live crawl, attach a CSV sample, and provide a brief performance summary.
* **Test a selector:** fetch once; report count, three text samples, first outerHTML; provide a repair hint with rationale.
* **Run at scale:** surface a settings diff (concurrency, throttling, retries) and a monitoring plan (logs, stats, alerts).

## 18. Quickstart Tasks

* Initialize the Scrapy project, baseline settings, and Typer CLI wrappers.
* Implement selector tools for explain and repair.
* Implement pipelines to normalize and serialize to the CSV contract.
* Add Dockerfile and optional Docker Compose with Scrapyd.
* Add tests, fixtures, and coverage config.
