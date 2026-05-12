import os
from pathlib import Path

SERVICE_NAME = os.environ.get("CATALOG_SERVICE_NAME", "catalog_service")
PORT = int(os.environ.get("CATALOG_PORT", "5001"))
DEFAULT_DB_PATH = Path(__file__).resolve().parent / "catalog.db"
DB_PATH = Path(os.environ.get("CATALOG_DB_PATH", DEFAULT_DB_PATH))
CATALOG_PEER_URL = os.environ.get("CATALOG_PEER_URL", "").strip()
