# Bazar.com Part 1 API Contract

This document describes the Part 1 HTTP API for Bazar.com. Routes are marked as **Implemented** or **Planned next**.

All responses are JSON. Common fields include `id`, `title`, `topic`, `price`, `quantity`, `item_id`, and `message`.

## Status codes used in Part 1

| Code | Meaning |
|------|---------|
| 200 | Successful read or update |
| 201 | Successful purchase |
| 400 | Bad input |
| 404 | Unknown item or topic |
| 409 | Out-of-stock purchase |

---

## Catalog service (port 5001)

### GET /search/\<topic\> — **Implemented**

**Purpose:** Return all books that match a topic.

**Success response (200):**

```json
[
  { "id": 1, "title": "How to get a good grade in DOS in 40 minutes a day" },
  { "id": 2, "title": "RPCs for Noobs" }
]
```

**Error response (404):**

```json
{ "message": "No books found for topic: <topic>" }
```

### GET /info/\<item_id\> — **Implemented**

**Purpose:** Return full details for one book.

**Success response (200):**

```json
{
  "id": 1,
  "title": "How to get a good grade in DOS in 40 minutes a day",
  "topic": "distributed systems",
  "price": 40,
  "quantity": 8
}
```

**Error responses:**

- `400` for a non-numeric `item_id`: `{ "message": "Invalid item_id" }`
- `404` for an unknown item: `{ "message": "Item not found: <item_id>" }`

### PUT /update/\<item_id\> — **Implemented**

**Purpose:** Update `price`, `quantity`, or both for one book.

**Request body examples:**

```json
{ "quantity": 4 }
```

```json
{ "price": 55 }
```

```json
{ "price": 55, "quantity": 4 }
```

**Success response (200):**

```json
{
  "message": "Item updated successfully",
  "item": {
    "id": 2,
    "title": "RPCs for Noobs",
    "topic": "distributed systems",
    "price": 55,
    "quantity": 4
  }
}
```

**Error responses:**

- `400` for missing body, empty body, missing fields, or invalid values
- `404` for an unknown item: `{ "message": "Item not found: <item_id>" }`

---

## Order service (port 5002) — **Planned next**

### POST /purchase/\<item_id\> — **Planned next**

**Purpose:** Check stock through the catalog service, decrement quantity when in stock, and write an order log entry.

**Success response (201):**

```json
{ "message": "Purchase successful", "item_id": 2 }
```

**Error responses:**

- `404` for an unknown item
- `409` when the item is out of stock

---

## Front-end service (port 5000) — **Planned next**

The front-end service is a Flask proxy. It does not call catalog or order services directly from the browser.

### GET /search/\<topic\> — **Planned next**

**Purpose:** Forward the request to the catalog service and return the catalog response.

### GET /info/\<item_id\> — **Planned next**

**Purpose:** Forward the request to the catalog service and return the catalog response.

### POST /purchase/\<item_id\> — **Planned next**

**Purpose:** Forward the request to the order service and return the order response.

Planned status codes follow the backend service that handles the request.
