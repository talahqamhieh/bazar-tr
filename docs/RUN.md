# Run Guide

How to run Bazar.com locally and in Docker. Use the front-end on port **5000** as the only client entry point for normal use.

All commands below assume you start from the **repository root** (the folder that contains `catalog_service`, `order_service`, `frontend_service`, and `docker-compose.yml`).

## Port summary

| Service | Default port |
|---------|----------------|
| Front-end | 5000 |
| Catalog | 5001 |
| Order | 5002 |
| Catalog replica 2 | 5011 |
| Order replica 2 | 5012 |

## Prerequisites

- Python 3.11 or newer
- `pip`
- Docker and Docker Compose (for containerized runs)

On Windows, use `py` if available; otherwise `python` or `python3`.

---

## Docker: full Lab 2 stack (recommended for grading)

Easiest way to run everything with replicas and cache:

```powershell
docker compose -f docker-compose.lab2.yml build
docker compose -f docker-compose.lab2.yml up
```

Client URL: **`http://127.0.0.1:5000`**

Background mode:

```powershell
docker compose -f docker-compose.lab2.yml up -d
```

Stop and remove volumes (fresh databases):

```powershell
docker compose -f docker-compose.lab2.yml down -v
```

**Startup order inside Compose:** catalog replicas → order replicas (depend on catalog) → front-end (depends on all). No manual ordering needed when using this file.

---

## Docker: Part 1 catalog only

`docker-compose.yml` runs the catalog service only:

```powershell
docker compose build catalog_service
docker compose up catalog_service
```

Front-end and order are not in this file; run them locally if needed.

Reset catalog volume:

```powershell
docker compose down -v
```

---

## Local Part 1 — three services

Open **three terminals** from the repository root.

**Terminal 1 — catalog**

```powershell
cd catalog_service
py -m pip install -r requirements.txt
py init_db.py
py app.py
```

**Terminal 2 — order**

```powershell
cd order_service
py -m pip install -r requirements.txt
$env:FRONTEND_INVALIDATION_URL = "http://127.0.0.1:5000"
py app.py
```

**Terminal 3 — front-end**

```powershell
cd frontend_service
py -m pip install -r requirements.txt
py app.py
```

Client URL: **`http://127.0.0.1:5000`**

### Smoke test

```powershell
curl.exe "http://127.0.0.1:5000/health"
curl.exe "http://127.0.0.1:5000/search/distributed%20systems"
curl.exe "http://127.0.0.1:5000/info/1"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/purchase/1"
```

---

## Local catalog only (Part 1 debugging)

```powershell
cd catalog_service
py -m pip install -r requirements.txt
py init_db.py
py app.py
```

Service: `http://127.0.0.1:5001`

`py init_db.py` creates the `books` table and seeds seven books. Default DB file: `catalog_service/catalog.db`.

### Catalog-only tests

```powershell
curl.exe "http://127.0.0.1:5001/search/distributed%20systems"
curl.exe "http://127.0.0.1:5001/info/1"
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:5001/update/2" -ContentType "application/json" -Body '{"price": 55}'
```

---

## Local Lab 2 — two catalog replicas

Use **two terminals**, both in `catalog_service`. Set variables **before** `init_db.py` and `app.py` so each replica uses its own database file.

**Replica 1 (port 5001)**

```powershell
cd catalog_service
$env:CATALOG_SERVICE_NAME = "catalog_service_1"
$env:CATALOG_DB_PATH = "catalog.db"
$env:CATALOG_PORT = "5001"
$env:CATALOG_PEER_URL = "http://127.0.0.1:5011"
py init_db.py
py app.py
```

**Replica 2 (port 5011)**

```powershell
cd catalog_service
$env:CATALOG_SERVICE_NAME = "catalog_service_2"
$env:CATALOG_DB_PATH = "catalog_replica_2.db"
$env:CATALOG_PORT = "5011"
$env:CATALOG_PEER_URL = "http://127.0.0.1:5001"
py init_db.py
py app.py
```

Public `PUT /update/<item_id>` on one replica syncs to the peer via `POST /internal/sync_update/<item_id>`.

---

## Local Lab 2 — two order replicas

Start at least one catalog instance first (e.g. replica 1 on **5001**). Use **two terminals** in `order_service`.

**Order replica 1 (port 5002)**

```powershell
cd order_service
$env:ORDER_SERVICE_NAME = "order_service_1"
$env:ORDER_DB_PATH = "orders.db"
$env:ORDER_PORT = "5002"
$env:CATALOG_SERVICE_URL = "http://127.0.0.1:5001"
$env:ORDER_PEER_URL = "http://127.0.0.1:5012"
$env:FRONTEND_INVALIDATION_URL = "http://127.0.0.1:5000"
py init_db.py
py app.py
```

**Order replica 2 (port 5012)**

```powershell
cd order_service
$env:ORDER_SERVICE_NAME = "order_service_2"
$env:ORDER_DB_PATH = "orders_replica_2.db"
$env:ORDER_PORT = "5012"
$env:CATALOG_SERVICE_URL = "http://127.0.0.1:5001"
$env:ORDER_PEER_URL = "http://127.0.0.1:5002"
$env:FRONTEND_INVALIDATION_URL = "http://127.0.0.1:5000"
py init_db.py
py app.py
```

---

## Local Lab 2 — front-end with replica routing

After catalog and order replicas are running:

```powershell
cd frontend_service
$env:CATALOG_REPLICA_URLS = "http://127.0.0.1:5001,http://127.0.0.1:5011"
$env:ORDER_REPLICA_URLS = "http://127.0.0.1:5002,http://127.0.0.1:5012"
py app.py
```

If those variables are unset, the front-end defaults to single Part 1 URLs (`5001`, `5002`).

### Cache timing demo

```powershell
curl.exe -i "http://127.0.0.1:5000/info/1"
curl.exe -i "http://127.0.0.1:5000/info/1"
```

See **`docs/PERFORMANCE.md`** for measured results.

---

## Recommended local startup order (Lab 2)

1. Catalog replica 1 and 2 (or single catalog on 5001 for simpler tests)
2. Order replica 1 and 2 (or single order on 5002)
3. Front-end (with `CATALOG_REPLICA_URLS` / `ORDER_REPLICA_URLS` when using replicas)
4. Run all client tests through port **5000** only

---

## More examples

| Resource | Purpose |
|----------|---------|
| `docs/SAMPLE_OUTPUT.md` | Captured terminal output |
| `tests/sample_requests.md` | Copy-paste curl commands |
| `tests/manual_test_checklist.md` | Manual validation checklist |
| `docs/API_CONTRACT.md` | HTTP API reference |
