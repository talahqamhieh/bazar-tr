# Sample Program Output

This file is a copy of output produced by running Bazar.com on a local Lab 2 stack (catalog replicas on **5001** / **5011**, order replicas on **5002** / **5012**, front-end on **5000**). Commands use PowerShell on Windows; `curl.exe` is used where response headers matter.

For how to reproduce these runs, see **`docs/RUN.md`**.

---

## Part 1 — Catalog service (direct, port 5001)

### Health check

```
> curl.exe "http://127.0.0.1:5001/health"
{"service":"catalog_service_1","status":"ok"}
```

### Search — topic `distributed systems`

```
> curl.exe "http://127.0.0.1:5001/search/distributed%20systems"
[{"id":1,"title":"How to get a good grade in DOS in 40 minutes a day"},{"id":2,"title":"RPCs for Noobs"},{"id":5,"title":"How to finish Project 3 on time"}]
```

### Search — topic `undergraduate school`

Returns books with IDs **3**, **4**, **6**, and **7** (four titles).

### Info — valid item

```
> curl.exe "http://127.0.0.1:5001/info/1"
{"id":1,"price":40,"quantity":6,"title":"How to get a good grade in DOS in 40 minutes a day","topic":"distributed systems"}
```

### Info — invalid item (404)

```
> curl.exe "http://127.0.0.1:5000/info/999"
{"message":"Item not found: 999"}
HTTP 404
```

### Update — catalog direct

```
> Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:5001/update/2" -ContentType "application/json" -Body '{"quantity": 4}'
{"message":"Item updated successfully","item":{"id":2,"price":50,"quantity":4,"title":"RPCs for Noobs","topic":"distributed systems"}}
```

---

## Part 1 — Integrated stack through front-end (port 5000)

### Health

```
> curl.exe "http://127.0.0.1:5000/health"
{"service":"frontend_service","status":"ok"}
```

### Search via front-end (first request — cache miss)

```
> curl.exe -i "http://127.0.0.1:5000/search/distributed%20systems"
HTTP/1.1 200 OK
Content-Type: application/json
X-Cache-Status: miss
X-Response-Time-Ms: 10.73

[{"id":1,"title":"How to get a good grade in DOS in 40 minutes a day"},{"id":2,"title":"RPCs for Noobs"},{"id":5,"title":"How to finish Project 3 on time"}]
```

---

## Lab 2 — Cache miss and cache hit

### Info — miss then hit (`GET /info/7`)

```
> curl.exe -i "http://127.0.0.1:5000/info/7"
HTTP/1.1 200 OK
X-Cache-Status: miss
X-Response-Time-Ms: 5.04
{"id":7,"price":20,"quantity":4,"title":"Spring in the Pioneer Valley","topic":"undergraduate school"}

> curl.exe -i "http://127.0.0.1:5000/info/7"
HTTP/1.1 200 OK
X-Cache-Status: hit
X-Response-Time-Ms: 0.00
{"id":7,"price":20,"quantity":4,"title":"Spring in the Pioneer Valley","topic":"undergraduate school"}
```

### Search — miss then hit

```
> curl.exe -i "http://127.0.0.1:5000/search/undergraduate%20school"
HTTP/1.1 200 OK
X-Cache-Status: miss
X-Response-Time-Ms: 10.50
[{"id":3,"title":"Xen and the Art of Surviving Undergraduate School"}, ...]

> curl.exe -i "http://127.0.0.1:5000/search/undergraduate%20school"
HTTP/1.1 200 OK
X-Cache-Status: hit
X-Response-Time-Ms: 0.00
[ same JSON body ]
```

---

## Lab 2 — Purchase and cache invalidation

### Successful purchase (201)

```
> curl.exe -s -w "\nHTTP %{http_code}\n" -X POST "http://127.0.0.1:5000/purchase/7"
{"item_id":7,"message":"Purchase successful"}
HTTP 201
```

### Info after purchase — cache miss with updated quantity

Quantity drops from **4** to **3**; front-end must fetch from catalog again:

```
> curl.exe -i "http://127.0.0.1:5000/info/7"
HTTP/1.1 200 OK
X-Cache-Status: miss
X-Response-Time-Ms: 2.31
{"id":7,"price":20,"quantity":3,"title":"Spring in the Pioneer Valley","topic":"undergraduate school"}
```

### Out of stock (409)

When `quantity` is 0, order service returns conflict:

```json
{"message": "Item out of stock", "item_id": 2}
```

---

## Lab 2 — Replicas

### Second catalog replica health (port 5011)

```
> curl.exe "http://127.0.0.1:5011/health"
{"service":"catalog_service_2","status":"ok"}
```

Catalog `PUT /update` on replica 1 updates local SQLite and sends `POST /internal/sync_update/<id>` to replica 2. Order purchases logged on replica 1 sync to replica 2 via `POST /internal/sync_order`. Sync success/failure is visible in service logs (see catalog/order log lines: `Sync request sent to peer`, `Sync applied successfully`).

---

## Front-end log lines (illustrative)

During the runs above, the front-end may log:

```
INFO:__main__:Cache miss for key info:7
INFO:__main__:Catalog request routed to catalog_service_1
INFO:__main__:Request completed in 5.04 ms (cache miss)
INFO:__main__:Cache hit for key info:7
INFO:__main__:Request completed in 0.00 ms (cache hit)
INFO:__main__:Purchase request bypasses cache
INFO:__main__:Invalidation request received for item_id 7
INFO:__main__:Cache entry removed for key info:7
INFO:__main__:Cleared 1 cached search entries
```

---

## Related documentation

| File | Content |
|------|---------|
| `docs/PERFORMANCE.md` | Measured cache timing tables and graphs |
| `docs/RUN.md` | Startup order and commands |
| `docs/API_CONTRACT.md` | Endpoints and status codes |
| `tests/sample_requests.md` | Copy-paste test commands |
