import logging
from urllib.parse import quote

from flask import Flask, jsonify

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


@app.get("/search/<topic>")
def search(topic):
    replica_name, base_url = catalog_balancer.next_replica()
    url = f"{base_url.rstrip('/')}/search/{quote(topic, safe='')}"
    logger.info("Incoming request: GET /search/%s", topic)
    logger.info("Catalog request routed to %s", replica_name)
    logger.info("Backend call target: GET %s", url)
    status_code, payload = forward_request("GET", url)
    return _proxy_response(status_code, payload)


@app.get("/info/<item_id>")
def info(item_id):
    replica_name, base_url = catalog_balancer.next_replica()
    url = f"{base_url.rstrip('/')}/info/{item_id}"
    logger.info("Incoming request: GET /info/%s", item_id)
    logger.info("Catalog request routed to %s", replica_name)
    logger.info("Backend call target: GET %s", url)
    status_code, payload = forward_request("GET", url)
    return _proxy_response(status_code, payload)


@app.post("/purchase/<item_id>")
def purchase(item_id):
    replica_name, base_url = order_balancer.next_replica()
    url = f"{base_url.rstrip('/')}/purchase/{item_id}"
    logger.info("Incoming request: POST /purchase/%s", item_id)
    logger.info("Order request routed to %s", replica_name)
    logger.info("Backend call target: POST %s", url)
    status_code, payload = forward_request("POST", url)
    return _proxy_response(status_code, payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
