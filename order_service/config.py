import os
from pathlib import Path

SERVICE_NAME = os.environ.get("ORDER_SERVICE_NAME", "order_service")
PORT = int(os.environ.get("ORDER_PORT", "5002"))
CATALOG_SERVICE_URL = os.environ.get("CATALOG_SERVICE_URL", "http://127.0.0.1:5001")
FRONTEND_INVALIDATION_URL = os.environ.get(
    "FRONTEND_INVALIDATION_URL",
    "http://127.0.0.1:5000",
)
DEFAULT_DB_PATH = Path(__file__).resolve().parent / "orders.db"
DB_PATH = Path(os.environ.get("ORDER_DB_PATH", DEFAULT_DB_PATH))
ORDER_PEER_URL = os.environ.get("ORDER_PEER_URL", "").strip()
