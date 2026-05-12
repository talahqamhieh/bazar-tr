import logging
from urllib.parse import quote

from flask import Flask, jsonify

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


def _proxy_response(status_code, payload):
    if status_code == 500 and payload.get("message") == "Backend service unavailable":
        logger.info("Backend failure: backend service unavailable")
        return jsonify(payload), status_code
    if status_code >= 400:
        logger.info("Backend failure: status %s", status_code)
    else:
        logger.info("Success response: status %s", status_code)
    return jsonify(payload), status_code


def _get_catalog_read(cache_key, log_label, build_url):
    cached = catalog_cache.get(cache_key)
    if cached is not None:
        status_code, payload = cached
        logger.info("Cache hit for key %s", cache_key)
        return _proxy_response(status_code, payload)

    logger.info("Cache miss for key %s", cache_key)
    replica_name, base_url = catalog_balancer.next_replica()
    url = build_url(base_url)
    logger.info("Catalog request routed to %s", replica_name)
    logger.info("Backend call target: GET %s", url)
    status_code, payload = forward_request("GET", url)
    catalog_cache.set(cache_key, status_code, payload)
    return _proxy_response(status_code, payload)


@app.get("/search/<topic>")
def search(topic):
    logger.info("Incoming request: GET /search/%s", topic)
    cache_key = search_cache_key(topic)
    return _get_catalog_read(
        cache_key,
        topic,
        lambda base_url: f"{base_url.rstrip('/')}/search/{quote(topic, safe='')}",
    )


@app.get("/info/<item_id>")
def info(item_id):
    logger.info("Incoming request: GET /info/%s", item_id)
    cache_key = info_cache_key(item_id)
    return _get_catalog_read(
        cache_key,
        item_id,
        lambda base_url: f"{base_url.rstrip('/')}/info/{item_id}",
    )


@app.post("/internal/invalidate/<item_id>")
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
    replica_name, base_url = order_balancer.next_replica()
    url = f"{base_url.rstrip('/')}/purchase/{item_id}"
    logger.info("Incoming request: POST /purchase/%s", item_id)
    logger.info("Purchase request bypasses cache")
    logger.info("Order request routed to %s", replica_name)
    logger.info("Backend call target: POST %s", url)
    status_code, payload = forward_request("POST", url)
    return _proxy_response(status_code, payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
