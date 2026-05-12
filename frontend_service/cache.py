class InMemoryCache:
    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, status_code, payload):
        self._store[key] = (status_code, payload)

    def invalidate_item(self, item_id):
        info_key = info_cache_key(item_id)
        removed_info = info_key in self._store
        if removed_info:
            del self._store[info_key]

        search_keys = [key for key in self._store if key.startswith("search:")]
        for key in search_keys:
            del self._store[key]

        return removed_info, len(search_keys)


catalog_cache = InMemoryCache()


def info_cache_key(item_id):
    return f"info:{item_id}"


def search_cache_key(topic):
    return f"search:{topic}"
