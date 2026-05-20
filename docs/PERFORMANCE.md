# Performance Experiments

This guide explains how to observe cache performance in the Bazar.com front-end service.

The front-end adds two response headers on catalog read requests:

- `X-Cache-Status`: `hit` or `miss`
- `X-Response-Time-Ms`: total front-end handling time in milliseconds

The JSON body is unchanged from the catalog service. Timing is in headers so the API payload stays the same while experiments stay easy to read.

## Why a cache hit is usually faster

On a **cache miss**, the front-end must:

1. Choose a catalog replica (round-robin)
2. Call the catalog service over HTTP
3. Wait for the response
4. Store the result in memory

On a **cache hit**, the front-end returns the stored JSON from memory and skips the catalog HTTP call. That is why the second read is usually much faster.

## Why invalidation causes a miss again

Before a purchase, the order service calls `POST /internal/invalidate/<item_id>` on the front-end. That removes the cached `info:<item_id>` entry and all cached `search:*` entries.

The next `GET /info/<item_id>` must contact the catalog again, so it becomes a **miss** and shows the updated quantity.

## Prerequisites

Run these services locally:

1. Catalog on port `5001`
2. Order on port `5002` with `FRONTEND_INVALIDATION_URL=http://127.0.0.1:5000`
3. Front-end on port `5000`

See `docs/RUN.md` for startup commands.

## Scenario 1: Info cache miss vs cache hit

```powershell
curl.exe -i "http://127.0.0.1:5000/info/1"
curl.exe -i "http://127.0.0.1:5000/info/1"
```

**Expected:**

- First response: `X-Cache-Status: miss` and a higher `X-Response-Time-Ms`
- Second response: `X-Cache-Status: hit` and a lower `X-Response-Time-Ms`

## Scenario 2: Search cache miss vs cache hit

```powershell
curl.exe -i "http://127.0.0.1:5000/search/distributed%20systems"
curl.exe -i "http://127.0.0.1:5000/search/distributed%20systems"
```

**Expected:**

- First response: `miss` with higher time
- Second response: `hit` with lower time

## Scenario 3: Invalidation after purchase

```powershell
curl.exe -i "http://127.0.0.1:5000/info/1"
curl.exe -i "http://127.0.0.1:5000/info/1"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/purchase/1"
curl.exe -i "http://127.0.0.1:5000/info/1"
```

**Expected:**

1. First `info/1`: `miss`
2. Second `info/1`: `hit`
3. Purchase: succeeds (`201`) and invalidates cache
4. Third `info/1`: `miss` again with updated `quantity` in the JSON body

## Reading headers in PowerShell

`curl.exe -i` prints response headers in the terminal.

You can also use:

```powershell
$r = Invoke-WebRequest -Uri "http://127.0.0.1:5000/info/1" -UseBasicParsing
$r.Headers["X-Cache-Status"]
$r.Headers["X-Response-Time-Ms"]
```

## Front-end logs

The front-end also logs lines such as:

- `Cache miss for key info:1`
- `Cache hit for key info:1`
- `Request completed in 2.15 ms (cache hit)`

Use logs together with headers when explaining results in a report or demo.

## What is not measured here

- No automated benchmark framework
- No load testing across many clients
- Purchase requests are timed in logs only (no cache headers)
- Replica synchronization timing is not included

This step focuses on simple, explainable cache behavior for the course project.
