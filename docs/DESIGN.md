# Bazar.com — Design Document

**Authors:** Talah Qamhieh, Rawan Al-Ahmad  
**Course:** Distributed and Operating Systems  
**Repository:** Bazar.com distributed online bookstore

This document describes the overall architecture, request flows, design tradeoffs, possible extensions, and how to run the system. Supporting material lives in `docs/SAMPLE_OUTPUT.md`, `docs/PERFORMANCE.md`, and `docs/RUN.md`.

---

## 1. Overall program design

Bazar.com is a small distributed bookstore built as three Flask microservices that communicate over HTTP with JSON payloads. Each service is a separate process (or container) with its own SQLite database where persistence is required.

| Service | Port(s) | Responsibility |
|---------|---------|----------------|
| `frontend_service` | 5000 | Single client entry point; read cache; round-robin to replicas; performance headers on reads |
| `catalog_service` | 5001, 5011 (replica) | Book inventory: search by topic, item info, quantity/price updates |
| `order_service` | 5002, 5012 (replica) | Purchases, order log, catalog stock checks, cache invalidation trigger |

**Part 1** delivers one instance of each service and local integration through the front-end. **Lab 2** adds two catalog replicas, two order replicas, peer synchronization, front-end caching with invalidation, and lightweight timing headers for experiments.

### Architecture diagram

```
                    Client (browser / curl / Postman)
                              |
                              v
                   +---------------------+
                   |  frontend_service   |
                   |  :5000              |
                   |  - in-memory cache  |
                   |  - round-robin      |
                   +----------+----------+
                              |
              +---------------+---------------+
              |                               |
              v                               v
    +------------------+            +------------------+
    | catalog_service  |            | order_service    |
    | :5001 / :5011    |<-----------| :5002 / :5012    |
    | SQLite (books)   |  HTTP PUT  | SQLite (orders)  |
    +--------+---------+            +--------+---------+
             |                                 |
             |  POST /internal/sync_update     |  POST /internal/sync_order
             v                                 v
    +------------------+            +------------------+
    | catalog peer     |            | order peer       |
    +------------------+            +------------------+
```

Clients never call catalog or order directly in normal use; they use `http://127.0.0.1:5000` (or the Docker-mapped front-end port).

### Data model

**Catalog (`books`):** `id`, `title`, `topic`, `price`, `quantity` — seven seed books (IDs 1–7) across topics `distributed systems` and `undergraduate school`.

**Order (`orders`):** `id`, `item_id`, `title`, `price_at_purchase`, `purchased_at` — append-only purchase log per order replica.

---

## 2. How it works

### 2.1 Read path (search / info)

1. Client sends `GET /search/<topic>` or `GET /info/<item_id>` to the front-end.
2. Front-end builds a cache key (`search:<topic>` or `info:<id>`).
3. **Cache hit:** return stored JSON immediately; set `X-Cache-Status: hit` and `X-Response-Time-Ms`.
4. **Cache miss:** pick the next catalog replica (round-robin), `GET` the catalog URL, store the response, return JSON with `X-Cache-Status: miss`.

Catalog replicas answer from their local SQLite file. In Lab 2, two replicas keep separate DB files; writes on one replica are pushed to the peer via `POST /internal/sync_update/<item_id>`.

### 2.2 Purchase path

1. Client sends `POST /purchase/<item_id>` to the front-end (no cache).
2. Front-end round-robins to an order replica.
3. Order service loads item info from catalog (`GET /info/<id>`).
4. If `quantity <= 0`, return **409** out of stock.
5. Order calls front-end `POST /internal/invalidate/<item_id>` to drop cached `info:` and all `search:` entries.
6. Order decrements quantity via catalog `PUT /update/<id>` with new quantity.
7. Order appends a row to its local `orders` table and syncs the row to the peer with `POST /internal/sync_order`.

Purchase always bypasses the read cache so stock changes are not served from stale cached JSON after invalidation.

### 2.3 Catalog update (admin / lab)

`PUT /update/<item_id>` accepts optional `price` and/or `quantity`. The receiving replica updates its DB, then forwards the same fields to the peer. Sync failures are logged; the handler still returns **200** for the local write (simplified fault model).

### 2.4 Internal endpoints (not for clients)

| Endpoint | Purpose |
|----------|---------|
| `POST /internal/invalidate/<item_id>` (front-end) | Remove cache entries after a purchase |
| `POST /internal/sync_update/<item_id>` (catalog) | Apply peer write to local DB |
| `POST /internal/sync_order` (order) | Copy purchase row to peer log |

### 2.5 Technology stack

- **Python 3.11**, **Flask**, **SQLite**, **Docker Compose**
- **urllib** for service-to-service HTTP (stdlib only, no extra HTTP client libraries)

---

## 3. Design tradeoffs

| Decision | Choice made | Alternative considered | Rationale |
|----------|-------------|------------------------|-----------|
| Communication | REST + JSON over HTTP | gRPC, message queues | Matches course tooling; easy to test with curl |
| Persistence | SQLite per service/replica | Shared PostgreSQL | Simple deployment; clear replica boundaries for Lab 2 |
| Load balancing | In-process round-robin | Nginx, consistent hashing | Minimal code; sufficient for demo and class scale |
| Cache | In-memory dict, no TTL | Redis, TTL-based expiry | Fast to implement; clearly shows hit vs miss in headers |
| Invalidation | Server-push from order before write | TTL only, client polling | Correctness after purchase; quantity visible on next read |
| Search invalidation | Clear all `search:*` on any item invalidation | Per-topic selective invalidation | Safer when quantity/price changes affect topic listings; simpler logic |
| Replication | Active sync on write (catalog + order) | Primary/replica with replication log | Understandable for a student project; mirrors “update peer now” mental model |
| Sync failure handling | Log and return local success | Two-phase commit, retries | Avoids blocking purchases on peer downtime; documented limitation |
| Performance measurement | Response headers on front-end reads | Full benchmark harness | Meets lab requirement without heavy infrastructure |
| Docker split | `docker-compose.yml` (catalog only) + `docker-compose.lab2.yml` (full stack) | Single compose file | Part 1 milestone stays small; Lab 2 stack is one command |

**Consistency model:** replicas are **eventually consistent**. A write succeeds locally even if peer sync fails; there is no distributed transaction. Last write wins per replica database.

**Cache vs direct catalog update:** invalidation is triggered from the order service during purchase. A direct `PUT /update` on catalog does not notify the front-end cache (documented simplification).

---

## 4. Possible improvements and extensions

1. **Retry with backoff** on peer sync and catalog calls from order service.
2. **Health-aware load balancing** — skip replicas that fail `/health`.
3. **Shared cache** (Redis) so multiple front-end instances stay coherent.
4. **TTL or versioning** on cache entries instead of invalidating all search keys.
5. **Invalidate front-end cache** when catalog receives `PUT /update` (callback or message).
6. **Idempotent purchase** with client request IDs to prevent duplicate orders on retries.
7. **Centralized metrics** (Prometheus) instead of header-only timing.
8. **Automated integration tests** in CI using Docker Compose and pytest/http client.
9. **Stronger consistency** — quorum writes or single primary catalog with read replicas.

These are out of scope for the current submission but follow naturally from the existing design.

---

## 5. How to run the program

Full step-by-step instructions are in **`docs/RUN.md`**. Summary:

### Prerequisites

- Python 3.11+
- `pip`
- Docker Desktop (optional, for containerized runs)

### Quickest verify (Docker — full Lab 2 stack)

From the repository root:

```powershell
docker compose -f docker-compose.lab2.yml build
docker compose -f docker-compose.lab2.yml up
```

Use **`http://127.0.0.1:5000`** for all client requests. Stop with `docker compose -f docker-compose.lab2.yml down` (add `-v` to reset databases).

### Local Part 1 (three terminals)

From the repository root, in separate terminals:

```powershell
cd catalog_service
py -m pip install -r requirements.txt
py init_db.py
py app.py
```

```powershell
cd order_service
py -m pip install -r requirements.txt
$env:FRONTEND_INVALIDATION_URL = "http://127.0.0.1:5000"
py app.py
```

```powershell
cd frontend_service
py -m pip install -r requirements.txt
py app.py
```

### Recommended startup order (Lab 2 local)

1. Catalog replica 1 (5001) and replica 2 (5011) — see `docs/RUN.md` for environment variables  
2. Order replica 1 (5002) and replica 2 (5012)  
3. Front-end with `CATALOG_REPLICA_URLS` and `ORDER_REPLICA_URLS`  
4. Test only through port **5000**

### Smoke test

```powershell
curl.exe "http://127.0.0.1:5000/health"
curl.exe "http://127.0.0.1:5000/info/1"
curl.exe -i "http://127.0.0.1:5000/info/1"
```

See **`docs/SAMPLE_OUTPUT.md`** for captured output and **`docs/PERFORMANCE.md`** for cache timing results.

---

## 6. Configuration reference

**Catalog:** `CATALOG_DB_PATH`, `CATALOG_SERVICE_NAME`, `CATALOG_PORT`, `CATALOG_PEER_URL`

**Order:** `ORDER_DB_PATH`, `ORDER_SERVICE_NAME`, `ORDER_PORT`, `CATALOG_SERVICE_URL`, `ORDER_PEER_URL`, `FRONTEND_INVALIDATION_URL`

**Front-end:** `CATALOG_REPLICA_URLS`, `ORDER_REPLICA_URLS` (comma-separated lists; fall back to single URLs)

## 7. Docker layout

- `docker-compose.yml` — Part 1 catalog service only  
- `docker-compose.lab2.yml` — two catalog replicas, two order replicas, front-end with replica URL lists

## 8. Known limitations (intentional)

- Round-robin only — no health checks  
- In-memory cache lost on front-end restart  
- No retry on peer sync failure  
- No conflict resolution — last write wins per replica DB  
- Direct catalog `PUT` does not invalidate front-end cache  
- Performance timing is illustrative (headers), not a formal benchmark suite

API details: **`docs/API_CONTRACT.md`**. Manual checklist: **`tests/manual_test_checklist.md`**.
