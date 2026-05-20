# Sample Requests

PowerShell examples. Quote paths if your folder name contains a comma.

## Part 1 — single stack (client uses port 5000)

```powershell
curl.exe "http://127.0.0.1:5000/search/distributed%20systems"
curl.exe "http://127.0.0.1:5000/info/1"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/purchase/1"
```

## Part 1 — catalog direct (port 5001)

```powershell
curl.exe "http://127.0.0.1:5001/search/distributed%20systems"
curl.exe "http://127.0.0.1:5001/info/1"
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:5001/update/2" -ContentType "application/json" -Body '{"quantity": 4}'
```

## Part 1 — order direct (port 5002)

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5002/purchase/1"
```

## Lab 2 — performance headers

```powershell
curl.exe -i "http://127.0.0.1:5000/info/1"
curl.exe -i "http://127.0.0.1:5000/info/1"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/purchase/1"
curl.exe -i "http://127.0.0.1:5000/info/1"
```

## Lab 2 — catalog replica sync check

```powershell
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:5001/update/5" -ContentType "application/json" -Body '{"quantity": 2}'
curl.exe "http://127.0.0.1:5011/info/5"
```

## Docker — Part 1 catalog

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2"
docker compose up -d catalog_service
curl.exe "http://127.0.0.1:5001/info/1"
docker compose down -v
```

## Docker — Lab 2 full stack

```powershell
docker compose -f docker-compose.lab2.yml up -d
curl.exe "http://127.0.0.1:5000/info/1"
docker compose -f docker-compose.lab2.yml down -v
```
