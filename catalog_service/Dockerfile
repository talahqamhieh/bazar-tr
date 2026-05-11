FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh

ENV CATALOG_DB_PATH=/data/catalog.db

EXPOSE 5001

ENTRYPOINT ["./entrypoint.sh"]
