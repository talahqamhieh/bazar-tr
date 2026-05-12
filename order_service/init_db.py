from db import init_db
from config import DB_PATH, SERVICE_NAME

if __name__ == "__main__":
    init_db()
    print(f"{SERVICE_NAME} database initialized at {DB_PATH}")
