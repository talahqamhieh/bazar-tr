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

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/RUN.md](docs/RUN.md) | How to run services locally and in Docker |
| [docs/API_CONTRACT.md](docs/API_CONTRACT.md) | HTTP API and status codes |
| [docs/DESIGN.md](docs/DESIGN.md) | Architecture and design choices |
| [docs/SAMPLE_OUTPUT.md](docs/SAMPLE_OUTPUT.md) | Example requests and responses |
| [docs/PERFORMANCE.md](docs/PERFORMANCE.md) | Cache timing experiments |
| [tests/manual_test_checklist.md](tests/manual_test_checklist.md) | Manual validation checklist |
| [tests/sample_requests.md](tests/sample_requests.md) | Copy-paste test commands |

## Quick start (Part 1 local)

Start catalog, order, and front-end in separate terminals, then use `http://127.0.0.1:5000` as the only client URL. See `docs/RUN.md` for exact commands.

## Known simplifications

This project uses beginner-friendly patterns: simple round-robin, in-memory cache only, peer sync without retries, and lightweight performance timing (not a full benchmark suite). See `docs/DESIGN.md` for details.
