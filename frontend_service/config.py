import os


def _parse_replica_urls(replicas_env, single_env, default_url):
    if replicas_env in os.environ:
        return [url.strip() for url in os.environ[replicas_env].split(",") if url.strip()]
    if single_env in os.environ:
        return [os.environ[single_env].strip()]
    return [default_url]


CATALOG_REPLICA_URLS = _parse_replica_urls(
    "CATALOG_REPLICA_URLS",
    "CATALOG_SERVICE_URL",
    "http://127.0.0.1:5001",
)
ORDER_REPLICA_URLS = _parse_replica_urls(
    "ORDER_REPLICA_URLS",
    "ORDER_SERVICE_URL",
    "http://127.0.0.1:5002",
)
