# Run Guide

This guide matches the current repository state. The catalog, order, and front-end services can be run locally for Part 1 integration testing. Docker currently supports the catalog service only.

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

`py init_db.py` creates the `books` table and inserts the four starter books. It also clears existing rows before re-seeding, so use it when you want a fresh local database.

By default, the SQLite file is stored at `catalog_service/catalog.db`.

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
py app.py
```

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2\frontend_service"
py -m pip install -r requirements.txt
py app.py
```

Use `http://127.0.0.1:5000` as the client entry point. The front-end forwards search and info requests to the catalog service and purchase requests to the order service.

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

## Later phases

`docker-compose.yml` includes commented placeholders for `frontend_service` and `order_service`. Those services are implemented locally, but they are not part of the current Docker workflow yet.

`docker-compose.lab2.yml` is a Lab 2 structure skeleton for a future one-frontend, two-catalog-replica, and two-order-replica setup. It is not runnable yet and should not be used for current Part 1 testing.
