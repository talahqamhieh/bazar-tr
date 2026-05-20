FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV CATALOG_DB_PATH=/data/catalog.db

EXPOSE 5001

CMD ["sh", "-c", "mkdir -p \"$(dirname \"$CATALOG_DB_PATH\")\" && if [ ! -f \"$CATALOG_DB_PATH\" ]; then python init_db.py; fi && exec python app.py"]
