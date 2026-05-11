# Part 1 Design

## Project overview

Bazar.com is a distributed online bookstore built for a university Distributed and Operating Systems project. Part 1 introduces three separate services that communicate over HTTP with JSON. Part 2 will later add replication, caching, consistency work, and performance measurements.

## Target Part 1 architecture

- **Front-end service (port 5000):** Receives client requests and forwards them to the correct backend service.
- **Catalog service (port 5001):** Stores books, answers search and info requests, and supports catalog updates.
- **Order service (port 5002):** Handles purchases, checks stock through the catalog service, updates quantity, and writes an order log.

## Current implementation status

- **Catalog service:** Complete for Part 1 catalog routes (`search`, `info`, `update`) with SQLite persistence.
- **Docker support:** Staged for the catalog service only, using a service Dockerfile, entrypoint, and root `docker-compose.yml`.
- **Front-end service:** Not implemented yet.
- **Order service:** Not implemented yet.

## Technology choices

- **Python 3.11**
- **Flask** for a lightweight web framework with simple REST routes
- **SQLite** for persistent on-disk storage in early Part 1 development
- **HTTP REST + JSON** for service communication
- **Docker Compose** for containerized deployment

These choices keep the project small, readable, and easy to explain while still supporting separate processes and later scaling work.

## Catalog data model

The catalog uses one SQLite table named `books` with:

- `id`
- `title`
- `topic`
- `price`
- `quantity`

The starter dataset contains four books with stable IDs from 1 to 4.

## Staged Docker approach

The repository currently containerizes only the implemented catalog service. That avoids pretending that missing services already work and keeps `docker compose up` valid for the current codebase.

The catalog container:

- installs Python dependencies from `requirements.txt`
- exposes port `5001`
- stores SQLite data on a named Docker volume
- initializes the database only when the database file does not exist yet

Commented service blocks in `docker-compose.yml` document how the front-end and order services will be added later.

## Incremental implementation plan

The project is being built in small verified steps:

1. Implement and test the catalog service on its own.
2. Add container support for the catalog service.
3. Add the order service and connect it to the catalog service.
4. Add the front-end proxy and run the full three-service Part 1 system.

This staged approach makes debugging easier because each service can be checked before integration.
