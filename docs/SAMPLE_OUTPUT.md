# Sample Output

Examples for Bazar.com. Direct catalog examples use port **5001**. Client examples use the front-end on port **5000**.

## Search distributed systems (7-book dataset)

```powershell
curl.exe "http://127.0.0.1:5001/search/distributed%20systems"
```

**Response (200):**

```json
[
  { "id": 1, "title": "How to get a good grade in DOS in 40 minutes a day" },
  { "id": 2, "title": "RPCs for Noobs" },
  { "id": 5, "title": "How to finish Project 3 on time" }
]
```

## Search undergraduate school

**Response (200):** books **3**, **4**, **6**, and **7**.

## Info for a valid item

```powershell
curl.exe "http://127.0.0.1:5001/info/1"
```

**Response (200):**

```json
{
  "id": 1,
  "price": 40,
  "quantity": 8,
  "title": "How to get a good grade in DOS in 40 minutes a day",
  "topic": "distributed systems"
}
```

## Info for an invalid item

**Response (404):** `{ "message": "Item not found: 999" }`

## Update (catalog direct)

```powershell
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:5001/update/2" -ContentType "application/json" -Body '{"quantity": 4}'
```

**Response (200):** `{ "message": "Item updated successfully", "item": { ... } }`

## Purchase through front-end

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/purchase/1"
```

**Response (201):**

```json
{ "message": "Purchase successful", "item_id": 1 }
```

## Out of stock

**Response (409):**

```json
{ "message": "Item out of stock", "item_id": 2 }
```

## Front-end read with performance headers

```powershell
curl.exe -i "http://127.0.0.1:5000/info/1"
```

Look for headers such as:

```
X-Cache-Status: miss
X-Response-Time-Ms: 42.50
```

Second request typically shows `hit` and a lower time. See `docs/PERFORMANCE.md`.
