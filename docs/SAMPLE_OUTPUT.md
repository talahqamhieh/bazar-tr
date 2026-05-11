# Sample Catalog Output

These examples match the current catalog service implementation on port `5001`.

## Search distributed systems

**Command:**

```powershell
curl.exe "http://127.0.0.1:5001/search/distributed%20systems"
```

**Response (200):**

```json
[
  { "id": 1, "title": "How to get a good grade in DOS in 40 minutes a day" },
  { "id": 2, "title": "RPCs for Noobs" }
]
```

## Search undergraduate school

**Command:**

```powershell
curl.exe "http://127.0.0.1:5001/search/undergraduate%20school"
```

**Response (200):**

```json
[
  { "id": 3, "title": "Xen and the Art of Surviving Undergraduate School" },
  { "id": 4, "title": "Cooking for the Impatient Undergrad" }
]
```

## Info for a valid item

**Command:**

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

**Command:**

```powershell
curl.exe "http://127.0.0.1:5001/info/999"
```

**Response (404):**

```json
{ "message": "Item not found: 999" }
```

## Update price only

**Command:**

```powershell
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:5001/update/2" -ContentType "application/json" -Body '{"price": 55}'
```

**Response (200):**

```json
{
  "item": {
    "id": 2,
    "price": 55,
    "quantity": 5,
    "title": "RPCs for Noobs",
    "topic": "distributed systems"
  },
  "message": "Item updated successfully"
}
```

## Update quantity only

**Command:**

```powershell
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:5001/update/2" -ContentType "application/json" -Body '{"quantity": 4}'
```

**Response (200):**

```json
{
  "item": {
    "id": 2,
    "price": 55,
    "quantity": 4,
    "title": "RPCs for Noobs",
    "topic": "distributed systems"
  },
  "message": "Item updated successfully"
}
```

## Update price and quantity

**Command:**

```powershell
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:5001/update/2" -ContentType "application/json" -Body '{"price": 55, "quantity": 4}'
```

**Response (200):**

```json
{
  "item": {
    "id": 2,
    "price": 55,
    "quantity": 4,
    "title": "RPCs for Noobs",
    "topic": "distributed systems"
  },
  "message": "Item updated successfully"
}
```

## Update invalid item

**Command:**

```powershell
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:5001/update/999" -ContentType "application/json" -Body '{"quantity": 4}'
```

**Response (404):**

```json
{ "message": "Item not found: 999" }
```
