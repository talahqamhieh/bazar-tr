# Performance Experiments and Results

This document reports **measured** front-end cache performance for Bazar.com Lab 2. Timing uses response headers on catalog read requests proxied through the front-end:

- `X-Cache-Status`: `hit` or `miss`
- `X-Response-Time-Ms`: total front-end handling time in milliseconds

Values below were collected on **21 May 2026** against a running local stack (front-end **5000**, catalog replicas **5001** / **5011**, order replicas **5002** / **5012**). Times vary with machine load; treat them as representative, not formal benchmarks.

---

## Results summary

| Scenario | Request | 1st call (cache) | 1st time (ms) | 2nd call (cache) | 2nd time (ms) |
|----------|---------|------------------|---------------|------------------|---------------|
| A | `GET /info/7` | miss | 5.04 | hit | 0.00 |
| B | `GET /search/undergraduate%20school` | miss | 10.50 | hit | 0.00 |
| C | `GET /search/distributed%20systems` | miss | 10.73 | hit | (not re-run; same pattern as B) |
| D | `GET /info/7` after `POST /purchase/7` | miss | 2.31 | — | — |

**Three-trial average** for `GET /info/1` after explicit invalidation (`POST /internal/invalidate/1` before each trial):

| Trial | Miss (ms) | Hit (ms) |
|-------|-----------|----------|
| 1 | 3.23 | 0.00 |
| 2 | 4.03 | 0.00 |
| 3 | 2.80 | 0.00 |
| **Average** | **3.35** | **0.00** |

### Brief explanation

- **Cache miss** includes round-robin replica selection plus an HTTP call to the catalog service. That extra network and JSON work explains higher times (roughly **3–11 ms** in these runs).
- **Cache hit** returns stored JSON from memory and skips the catalog HTTP call, so times are effectively **0.00 ms** at the millisecond precision used in headers.
- **After purchase**, invalidation removes `info:<id>` and all `search:*` entries; the next `GET /info/<id>` is a **miss** again and shows the decremented `quantity` in the body (e.g. 4 → 3 for item 7).

---

## Comparison table (miss vs hit)

| Endpoint | Avg miss (ms) | Avg hit (ms) | Speedup (miss ÷ hit)* |
|----------|---------------|--------------|------------------------|
| `/info/1` (3 trials) | 3.35 | 0.00 | N/A† |
| `/info/7` (single pair) | 5.04 | 0.00 | N/A† |
| `/search/undergraduate school` | 10.50 | 0.00 | N/A† |

† Hit times round to 0.00 ms in headers; speedup is “large” in relative terms but not a precise ratio here.

---

## ASCII chart — `GET /info/1` (average ms, 3 trials)

```
miss ████████████████████  3.35 ms
hit  ·                      0.00 ms
     0    1    2    3    4    5 ms
```

## ASCII chart — single-run pairs

```
/info/7        miss ██████████ 5.04 ms    hit · 0.00 ms
/search/...    miss █████████████████████ 10.50 ms   hit · 0.00 ms
/info/7 post-  miss █████ 2.31 ms  (invalidation + catalog fetch)
purchase
```

---

## How to reproduce

### Prerequisites

1. Catalog on **5001** (and **5011** for Lab 2 replicas)
2. Order on **5002** with `FRONTEND_INVALIDATION_URL=http://127.0.0.1:5000`
3. Front-end on **5000**

See **`docs/RUN.md`** for startup commands. Docker option:

```powershell
docker compose -f docker-compose.lab2.yml up
```

### Scenario 1: Info cache miss vs hit

```powershell
curl.exe -i "http://127.0.0.1:5000/info/7"
curl.exe -i "http://127.0.0.1:5000/info/7"
```

### Scenario 2: Search cache miss vs hit

```powershell
curl.exe -i "http://127.0.0.1:5000/search/undergraduate%20school"
curl.exe -i "http://127.0.0.1:5000/search/undergraduate%20school"
```

### Scenario 3: Invalidation after purchase

```powershell
curl.exe -i "http://127.0.0.1:5000/info/7"
curl.exe -i "http://127.0.0.1:5000/info/7"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/purchase/7"
curl.exe -i "http://127.0.0.1:5000/info/7"
```

Expected: miss → hit → purchase **201** → miss with lower `quantity`.

### Three-trial average (optional)

```powershell
foreach ($i in 1..3) {
  Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/internal/invalidate/1" | Out-Null
  $miss = Invoke-WebRequest -Uri "http://127.0.0.1:5000/info/1" -UseBasicParsing
  $hit  = Invoke-WebRequest -Uri "http://127.0.0.1:5000/info/1" -UseBasicParsing
  "$i miss=$($miss.Headers['X-Response-Time-Ms']) hit=$($hit.Headers['X-Response-Time-Ms'])"
}
```

---

## Why a cache hit is usually faster

On a **cache miss**, the front-end:

1. Chooses a catalog replica (round-robin)
2. Calls the catalog service over HTTP
3. Waits for the response
4. Stores the result in memory

On a **cache hit**, the front-end returns stored JSON and skips step 2–3.

---

## Why invalidation causes a miss again

Before a purchase, the order service calls `POST /internal/invalidate/<item_id>` on the front-end. That removes `info:<item_id>` and all cached `search:*` keys. The next read must contact the catalog again (**miss**) and reflects updated inventory.

---

## Reading headers in PowerShell

```powershell
$r = Invoke-WebRequest -Uri "http://127.0.0.1:5000/info/1" -UseBasicParsing
$r.Headers["X-Cache-Status"]
$r.Headers["X-Response-Time-Ms"]
```

Or use `curl.exe -i` to print headers in the terminal.

---

## What is not measured here

- No automated load-testing framework or multi-client stress test
- Purchase latency is logged in the front-end only (no cache headers on `POST /purchase`)
- Peer synchronization timing is not included in these tables
- Results depend on localhost networking and current DB state

This scope matches the course requirement for simple, explainable cache measurements rather than a full performance study.
