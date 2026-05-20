# Run Guide

How to run Bazar.com locally and in Docker. Use the front-end on port **5000** as the only client entry point for normal use.

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
- Docker and Docker Compose for containerized runs

## Run the catalog service locally

From the repository root:

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\catalog_service"
py -m pip install -r requirements.txt
py init_db.py
py app.py
```

The service listens on `http://127.0.0.1:5001`.

If `py` is not available on your machine, use `python` or `python3` with the same commands.

## Initialize the catalog database locally

`py init_db.py` creates the `books` table and inserts the seven starter books. It also clears existing rows before re-seeding, so use it when you want a fresh local database.

By default, the SQLite file is stored at `catalog_service/catalog.db`.

## Run two local catalog replicas (Lab 2)

Use two terminals in `catalog_service`. Set the environment variables first, then initialize and start each replica.

Replica 1:

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\catalog_service"
$env:CATALOG_SERVICE_NAME = "catalog_service_1"
$env:CATALOG_DB_PATH = "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\catalog_service\catalog.db"
$env:CATALOG_PORT = "5001"
$env:CATALOG_PEER_URL = "http://127.0.0.1:5011"
py init_db.py
py app.py
```

Replica 2:

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\catalog_service"
$env:CATALOG_SERVICE_NAME = "catalog_service_2"
$env:CATALOG_DB_PATH = "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\catalog_service\catalog_replica_2.db"
$env:CATALOG_PORT = "5011"
$env:CATALOG_PEER_URL = "http://127.0.0.1:5001"
py init_db.py
py app.py
```

Each replica keeps its own SQLite file. Set `CATALOG_PEER_URL` to the other replica's base URL so public `PUT /update/<item_id>` writes sync to the peer through `POST /internal/sync_update/<item_id>`.

To reinitialize one replica, run `py init_db.py` again in that replica's terminal with the same environment variables.

## Run two local order replicas (Lab 2)

Start one catalog service first, for example replica 1 on port `5001`. Then use two terminals in `order_service`.

Order replica 1:

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\order_service"
$env:ORDER_SERVICE_NAME = "order_service_1"
$env:ORDER_DB_PATH = "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\order_service\orders.db"
$env:ORDER_PORT = "5002"
$env:CATALOG_SERVICE_URL = "http://127.0.0.1:5001"
$env:ORDER_PEER_URL = "http://127.0.0.1:5012"
$env:FRONTEND_INVALIDATION_URL = "http://127.0.0.1:5000"
py init_db.py
py app.py
```

Order replica 2:

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\order_service"
$env:ORDER_SERVICE_NAME = "order_service_2"
$env:ORDER_DB_PATH = "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\order_service\orders_replica_2.db"
$env:ORDER_PORT = "5012"
$env:CATALOG_SERVICE_URL = "http://127.0.0.1:5001"
$env:ORDER_PEER_URL = "http://127.0.0.1:5002"
$env:FRONTEND_INVALIDATION_URL = "http://127.0.0.1:5000"
py init_db.py
py app.py
```

Each order replica keeps its own SQLite log file. Set `ORDER_PEER_URL` to the other replica's base URL so successful purchases sync to the peer through `POST /internal/sync_order`.

To reinitialize one order replica database, run `py init_db.py` again in that replica's terminal with the same environment variables.

## Test the catalog service locally

With the service running, try:

```powershell
curl.exe "http://127.0.0.1:5001/search/distributed%20systems"
curl.exe "http://127.0.0.1:5001/info/1"
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:5001/update/2" -ContentType "application/json" -Body '{"price": 55}'
```

More examples are in `tests/sample_requests.md` and `docs/SAMPLE_OUTPUT.md`.

## Run the full local Part 1 stack

Start each service in its own terminal:

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\catalog_service"
py -m pip install -r requirements.txt
py init_db.py
py app.py
```

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\order_service"
py -m pip install -r requirements.txt
$env:FRONTEND_INVALIDATION_URL = "http://127.0.0.1:5000"
py app.py
```

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\frontend_service"
py -m pip install -r requirements.txt
py app.py
```

Use `http://127.0.0.1:5000` as the client entry point. The front-end forwards search and info requests to the catalog service and purchase requests to the order service.

## Run the front-end with replica round-robin (Lab 2)

After the catalog and order replicas are running, start the front-end with replica URL lists:

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\frontend_service"
$env:CATALOG_REPLICA_URLS = "http://127.0.0.1:5001,http://127.0.0.1:5011"
$env:ORDER_REPLICA_URLS = "http://127.0.0.1:5002,http://127.0.0.1:5012"
py app.py
```

If those env vars are not set, the front-end still defaults to the single Part 1 URLs on ports `5001` and `5002`.

The front-end keeps an in-memory cache for catalog read responses (`GET /info/<item_id>` and `GET /search/<topic>`). Before a purchase updates catalog quantity, the order service calls `POST /internal/invalidate/<item_id>` on the front-end. Search cache entries are cleared on invalidation because quantity or price changes can make topic search results stale.

For cache timing experiments, see `docs/PERFORMANCE.md`. Read responses include `X-Cache-Status` and `X-Response-Time-Ms` headers.

## Test the integrated local stack through the front-end

```powershell
curl.exe "http://127.0.0.1:5000/search/distributed%20systems"
curl.exe "http://127.0.0.1:5000/info/1"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/purchase/1"
```

## Build and run the catalog service with Docker

From the repository root:

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2"
docker compose build catalog_service
docker compose up catalog_service
```

Run in the background:

```powershell
docker compose up -d catalog_service
```

Stop the container:

```powershell
docker compose down
```

The container entrypoint creates `/data/catalog.db` on first startup if the database file does not exist yet. Later restarts reuse the existing database in the Docker volume.

## Reset Docker catalog data

To remove the catalog volume and start with a fresh database on the next startup:

```powershell
docker compose down -v
```

To re-seed manually inside a one-off container:

```powershell
docker compose run --rm catalog_service python init_db.py
```

## Docker: Part 1 catalog only

`docker-compose.yml` runs the catalog service only. Front-end and order are implemented locally but not in that file.

## Docker: full Lab 2 stack

From the repository root:

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2"
docker compose -f docker-compose.lab2.yml build
docker compose -f docker-compose.lab2.yml up
```

Client URL: `http://127.0.0.1:5000`

Stop and remove volumes:

```powershell
docker compose -f docker-compose.lab2.yml down -v
```

## Recommended local startup order (Lab 2 demo)

1. Catalog replica 1 and 2 (or single catalog on 5001 for simpler tests)
2. Order replica 1 and 2 (or single order on 5002)
3. Front-end with `CATALOG_REPLICA_URLS` and `ORDER_REPLICA_URLS` if using replicas
4. Run tests through port **5000** only
