import logging
import time
from urllib.parse import quote

from flask import Flask, jsonify, make_response

from cache import catalog_cache, info_cache_key, search_cache_key
from client import forward_request
from config import CATALOG_REPLICA_URLS, ORDER_REPLICA_URLS
from load_balancer import RoundRobin

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

catalog_balancer = RoundRobin(CATALOG_REPLICA_URLS, "catalog_service")
order_balancer = RoundRobin(ORDER_REPLICA_URLS, "order_service")


@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Not found"}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"message": "Bad request"}), 400


@app.errorhandler(500)
def server_error(error):
    return jsonify({"message": "Internal server error"}), 500


@app.get("/")
def home():
    return jsonify({"service": "frontend_service", "status": "running"}), 200


@app.get("/health")
def health():
    return jsonify({"service": "frontend_service", "status": "ok"}), 200


def _make_json_response(status_code, payload, cache_status=None, response_time_ms=None):
    response = make_response(jsonify(payload), status_code)
    if cache_status is not None:
        response.headers["X-Cache-Status"] = cache_status
    if response_time_ms is not None:
        response.headers["X-Response-Time-Ms"] = f"{response_time_ms:.2f}"
        logger.info(
            "Request completed in %.2f ms (cache %s)",
            response_time_ms,
            cache_status,
        )
    if status_code >= 400:
        logger.info("Backend failure: status %s", status_code)
    elif cache_status is None:
        logger.info("Success response: status %s", status_code)
    return response


def _get_catalog_read(cache_key, build_url):
    start = time.perf_counter()
    cached = catalog_cache.get(cache_key)
    if cached is not None:
        status_code, payload = cached
        elapsed_ms = (time.perf_counter() - start) * 1000 # time after hit 
        logger.info("Cache hit for key %s", cache_key)
        return _make_json_response(status_code, payload, "hit", elapsed_ms)

    logger.info("Cache miss for key %s", cache_key)
    replica_name, base_url = catalog_balancer.next_replica()
    url = build_url(base_url)
    logger.info("Catalog request routed to %s", replica_name)
    logger.info("Backend call target: GET %s", url)
    status_code, payload = forward_request("GET", url)
    catalog_cache.set(cache_key, status_code, payload)
    elapsed_ms = (time.perf_counter() - start) * 1000 # time after miss
    return _make_json_response(status_code, payload, "miss", elapsed_ms)


@app.get("/search/<topic>")
def search(topic):
    logger.info("Incoming request: GET /search/%s", topic)
    cache_key = search_cache_key(topic)
    return _get_catalog_read(
        cache_key,
        lambda base_url: f"{base_url.rstrip('/')}/search/{quote(topic, safe='')}",
    )


@app.get("/info/<item_id>")
def info(item_id):
    logger.info("Incoming request: GET /info/%s", item_id)
    cache_key = info_cache_key(item_id)
    return _get_catalog_read(
        cache_key,
        lambda base_url: f"{base_url.rstrip('/')}/info/{item_id}",
    )


@app.post("/internal/invalidate/<item_id>") # invalidate cache 
def invalidate(item_id):
    logger.info("Invalidation request received for item_id %s", item_id)
    if not item_id.isdigit():
        return jsonify({"message": "Invalid item_id"}), 400

    removed_info, removed_search_count = catalog_cache.invalidate_item(item_id)
    if removed_info:
        logger.info("Cache entry removed for key %s", info_cache_key(item_id))
    else:
        logger.info("Cache key not present for key %s", info_cache_key(item_id))
    if removed_search_count:
        logger.info("Cleared %d cached search entries", removed_search_count)

    return jsonify({"message": "Cache invalidated", "item_id": int(item_id)}), 200


@app.post("/purchase/<item_id>")
def purchase(item_id):
    start = time.perf_counter()
    replica_name, base_url = order_balancer.next_replica()
    url = f"{base_url.rstrip('/')}/purchase/{item_id}"
    logger.info("Incoming request: POST /purchase/%s", item_id)
    logger.info("Purchase request bypasses cache")
    logger.info("Order request routed to %s", replica_name)
    logger.info("Backend call target: POST %s", url)
    status_code, payload = forward_request("POST", url)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("Purchase request completed in %.2f ms", elapsed_ms)
    return _make_json_response(status_code, payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
