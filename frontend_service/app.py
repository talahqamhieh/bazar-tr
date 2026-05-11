import logging
from urllib.parse import quote

from flask import Flask, jsonify

from client import forward_request
from config import CATALOG_SERVICE_URL, ORDER_SERVICE_URL

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    url = f"{CATALOG_SERVICE_URL.rstrip('/')}/search/{quote(topic, safe='')}"
    logger.info("Incoming request: GET /search/%s", topic)
    logger.info("Backend call target: GET %s", url)
    status_code, payload = forward_request("GET", url)
    return _proxy_response(status_code, payload)


@app.get("/info/<item_id>")
def info(item_id):
    url = f"{CATALOG_SERVICE_URL.rstrip('/')}/info/{item_id}"
    logger.info("Incoming request: GET /info/%s", item_id)
    logger.info("Backend call target: GET %s", url)
    status_code, payload = forward_request("GET", url)
    return _proxy_response(status_code, payload)


@app.post("/purchase/<item_id>")
def purchase(item_id):
    url = f"{ORDER_SERVICE_URL.rstrip('/')}/purchase/{item_id}"
    logger.info("Incoming request: POST /purchase/%s", item_id)
    logger.info("Backend call target: POST %s", url)
    status_code, payload = forward_request("POST", url)
    return _proxy_response(status_code, payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
