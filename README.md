# Bazar.com

Distributed online bookstore for a university Distributed and Operating Systems project.

## What is implemented

**Part 1**

- `catalog_service` — search, info, update, SQLite persistence (port **5001**)
- `order_service` — purchase flow, order log, catalog integration (port **5002**)
- `frontend_service` — client entry point, proxies to catalog and order (port **5000**)
- Local three-service integration through the front-end
- Staged Docker support for the catalog (`docker-compose.yml`)

**Lab 2**

- Seven-book catalog dataset (IDs 1–7)
- Two runnable catalog replicas with peer sync
- Two runnable order replicas with peer sync
- Front-end round-robin routing to replicas
- In-memory read cache with invalidation before writes
- Performance timing headers on read responses
- Full Lab 2 stack in `docker-compose.lab2.yml`

## Documentation (submission)

All professor-required deliverables are under **`docs/`**:

| Document | Purpose |
|----------|---------|
| [docs/DESIGN.md](docs/DESIGN.md) | **Design document** (~2–3 pages): architecture, tradeoffs, extensions, how to run |
| [docs/SAMPLE_OUTPUT.md](docs/SAMPLE_OUTPUT.md) | **Program output** captured from real runs |
| [docs/PERFORMANCE.md](docs/PERFORMANCE.md) | **Performance results** (tables + ASCII charts) |
| [docs/RUN.md](docs/RUN.md) | Step-by-step run instructions (local + Docker) |
| [docs/API_CONTRACT.md](docs/API_CONTRACT.md) | HTTP API and status codes |
| [tests/manual_test_checklist.md](tests/manual_test_checklist.md) | Manual validation checklist |
| [tests/sample_requests.md](tests/sample_requests.md) | Copy-paste test commands |

Source code includes inline comments in service modules (catalog, order, front-end cache and routing).

## Quick start

**Docker (full Lab 2):** from repo root, `docker compose -f docker-compose.lab2.yml up` — client URL `http://127.0.0.1:5000`.

**Local Part 1:** start catalog, order, and front-end in separate terminals; see `docs/RUN.md` for exact commands.

## Known simplifications

This project uses beginner-friendly patterns: simple round-robin, in-memory cache only, peer sync without retries, and lightweight performance timing (not a full benchmark suite). See `docs/DESIGN.md` for details.
