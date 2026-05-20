# Bazar.com API Contract

All public responses are JSON unless noted. Common fields: `id`, `title`, `topic`, `price`, `quantity`, `item_id`, `message`.

## Status codes

| Code | Meaning |
|------|---------|
| 200 | Successful read or update |
| 201 | Successful purchase |
| 400 | Bad input |
| 404 | Unknown item or topic |
| 409 | Out-of-stock purchase |
| 500 | Backend or service error |

## Service ports (default local)

| Service | Port |
|---------|------|
| Front-end | 5000 |
| Catalog | 5001 |
| Order | 5002 |
| Catalog replica 2 | 5011 |
| Order replica 2 | 5012 |

---

## Front-end service (port 5000)

The client talks only to the front-end. It forwards requests to catalog and order services.

### GET /search/\<topic\>

Forwards to a catalog replica. Returns the catalog JSON body unchanged.

**Read response headers (Lab 2):**

- `X-Cache-Status`: `hit` or `miss`
- `X-Response-Time-Ms`: front-end handling time in milliseconds

### GET /info/\<item_id\>

Forwards to a catalog replica. Same timing headers as search.

### POST /purchase/\<item_id\>

Forwards to an order replica. Does not use the read cache. No cache timing headers.

Status codes match the order service response.

---

## Catalog service (port 5001)

### GET /search/\<topic\>

**Success (200):** JSON array of `{ "id", "title" }` only.

**Error (404):**

```json
{ "message": "No books found for topic: <topic>" }
```

With the seven-book dataset, `distributed systems` returns books **1**, **2**, and **5**.

### GET /info/\<item_id\>

**Success (200):**

```json
{
  "id": 1,
  "title": "How to get a good grade in DOS in 40 minutes a day",
  "topic": "distributed systems",
  "price": 40,
  "quantity": 8
}
```

**Errors:** `400` invalid `item_id`; `404` item not found.

### PUT /update/\<item_id\>

Updates `price`, `quantity`, or both. Syncs to peer catalog replica when `CATALOG_PEER_URL` is set.

**Success (200):**

```json
{
  "message": "Item updated successfully",
  "item": { "id": 2, "title": "...", "topic": "...", "price": 55, "quantity": 4 }
}
```

### POST /internal/sync_update/\<item_id\> (internal, Lab 2)

Used between catalog replicas. Same body as public update. Does not re-sync to avoid loops.

---

## Order service (port 5002)

### POST /purchase/\<item_id\>

Checks catalog stock, invalidates front-end cache, decrements catalog quantity, logs order locally, syncs log to peer when `ORDER_PEER_URL` is set.

**Success (201):**

```json
{ "message": "Purchase successful", "item_id": 2 }
```

**Errors:** `400` invalid `item_id`; `404` item not found; `409` out of stock; `500` catalog or service error.

### POST /internal/sync_order (internal, Lab 2)

**Body:**

```json
{
  "item_id": 2,
  "title": "RPCs for Noobs",
  "price_at_purchase": 50,
  "purchased_at": "2026-05-12T12:00:00+00:00"
}
```

Stores a successful purchase row on the peer without re-syncing.

---

## Front-end internal (Lab 2)

### POST /internal/invalidate/\<item_id\>

Called by the order service before a catalog write. Removes `info:<item_id>` and all cached `search:*` entries.

**Success (200):**

```json
{ "message": "Cache invalidated", "item_id": 1 }
```

---

## Starter books (IDs 1–7)

| ID | Title | Topic |
|----|-------|-------|
| 1 | How to get a good grade in DOS in 40 minutes a day | distributed systems |
| 2 | RPCs for Noobs | distributed systems |
| 3 | Xen and the Art of Surviving Undergraduate School | undergraduate school |
| 4 | Cooking for the Impatient Undergrad | undergraduate school |
| 5 | How to finish Project 3 on time | distributed systems |
| 6 | Why theory classes are so hard | undergraduate school |
| 7 | Spring in the Pioneer Valley | undergraduate school |
