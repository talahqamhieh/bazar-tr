import os

CATALOG_SERVICE_URL = os.environ.get("CATALOG_SERVICE_URL", "http://127.0.0.1:5001")
ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://127.0.0.1:5002")
