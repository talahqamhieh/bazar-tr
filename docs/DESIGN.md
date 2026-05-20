# Bazar.com Design

## Project overview

Bazar.com is a distributed online bookstore built for a university Distributed and Operating Systems course. The system uses three Flask microservices that communicate over HTTP with JSON, plus SQLite for persistence.

## Architecture

```
Client
  |
  v
frontend_service :5000  (cache, round-robin, timing headers)
  |                    \
  |                     --> order_service :5002 (or :5012 replica)
  v
catalog_service :5001  (or :5011 replica)
```

- **Front-end (5000):** Single client entry point. Proxies reads to catalog replicas and purchases to order replicas.
- **Catalog (5001 / 5011):** Book inventory, search, info, updates.
- **Order (5002 / 5012):** Purchases, order log, catalog stock checks.

## Part 1 (complete)

- Three services as separate processes
- REST + JSON APIs
- Front-end proxies all client traffic
- Catalog Docker via `docker-compose.yml` (catalog only)

## Lab 2 (complete)

| Feature | Approach |
|---------|----------|
| Dataset | Seven books (IDs 1–7) |
| Catalog replicas | Same code, different `CATALOG_DB_PATH` and ports |
| Order replicas | Same code, different `ORDER_DB_PATH` and ports |
| Load balancing | Simple in-memory round-robin in front-end |
| Cache | In-memory dict for `info:` and `search:` keys |
| Invalidation | Order calls `POST /internal/invalidate/<item_id>` before catalog write |
| Catalog sync | `PUT /update` forwards to peer `POST /internal/sync_update` |
| Order sync | After local log, `POST /internal/sync_order` to peer |
| Performance | `X-Cache-Status` and `X-Response-Time-Ms` headers on reads |

## Technology choices

- **Python 3.11**, **Flask**, **SQLite**, **Docker Compose**
- **urllib** for service-to-service HTTP (no extra client libraries)

## Catalog data model

Table `books`: `id`, `title`, `topic`, `price`, `quantity`.

Order table `orders`: `id`, `item_id`, `title`, `price_at_purchase`, `purchased_at`.

## Known limitations (intentional)

These are simplified by design for a student project:

- **Round-robin only** — no health checks or weighted routing
- **In-memory cache** — lost on front-end restart; no TTL
- **No retry on peer sync** — local write succeeds even if peer sync fails (logged)
- **No conflict resolution** — last write wins per replica DB
- **Cache invalidation** — server-push from order only; direct catalog `PUT` does not invalidate front-end cache
- **Performance timing** — lightweight headers, not a full benchmarking framework
- **Docker** — `docker-compose.yml` is catalog-only; full stack uses `docker-compose.lab2.yml` locally or in Docker

## Configuration (environment variables)

**Catalog:** `CATALOG_DB_PATH`, `CATALOG_SERVICE_NAME`, `CATALOG_PORT`, `CATALOG_PEER_URL`

**Order:** `ORDER_DB_PATH`, `ORDER_SERVICE_NAME`, `ORDER_PORT`, `CATALOG_SERVICE_URL`, `ORDER_PEER_URL`, `FRONTEND_INVALIDATION_URL`

**Front-end:** `CATALOG_REPLICA_URLS`, `ORDER_REPLICA_URLS` (comma-separated; falls back to single URLs)

## Docker layout

- `docker-compose.yml` — catalog service for Part 1
- `docker-compose.lab2.yml` — catalog replicas, order replicas, front-end with replica URLs
