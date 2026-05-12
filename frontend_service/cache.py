class InMemoryCache:
    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, status_code, payload):
        self._store[key] = (status_code, payload)


catalog_cache = InMemoryCache()


def info_cache_key(item_id):
    return f"info:{item_id}"


def search_cache_key(topic):
    return f"search:{topic}"
