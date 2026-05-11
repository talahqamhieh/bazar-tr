# Sample Requests

Use these commands after the catalog service is running.

## Local catalog testing

From PowerShell:

```powershell
curl.exe "http://127.0.0.1:5001/search/distributed%20systems"
curl.exe "http://127.0.0.1:5001/search/undergraduate%20school"
curl.exe "http://127.0.0.1:5001/search/unknown-topic"
curl.exe "http://127.0.0.1:5001/info/1"
curl.exe "http://127.0.0.1:5001/info/999"
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:5001/update/2" -ContentType "application/json" -Body '{"price": 55}'
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:5001/update/2" -ContentType "application/json" -Body '{"quantity": 4}'
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:5001/update/2" -ContentType "application/json" -Body '{"price": 55, "quantity": 4}'
```

If you prefer `curl.exe` for updates in PowerShell, use the stop-parsing operator:

```powershell
curl.exe --% -X PUT -H "Content-Type: application/json" --data-raw "{\"price\": 55}" http://127.0.0.1:5001/update/2
```

## Docker catalog testing

Start the container from the repository root:

```powershell
cd "c:\Users\Talah Qamhieh\OneDrive\Desktop\dos\part1, 2"
docker compose up -d catalog_service
```

Then run the same request examples against `http://127.0.0.1:5001`.

Stop and remove the catalog volume:

```powershell
docker compose down -v
```
