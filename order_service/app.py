import logging
import os

from flask import Flask, jsonify

from client import get_item_info, update_item_quantity
from db import init_db, log_purchase

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATALOG_SERVICE_URL = os.environ.get("CATALOG_SERVICE_URL", "http://127.0.0.1:5001")

init_db()


@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Not found"}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"message": "Bad request"}), 400


@app.errorhandler(500)
def server_error(error):
    return jsonify({"message": "Internal server error"}), 500


@app.post("/purchase/<item_id>")
def purchase(item_id):
    logger.info("Incoming request: POST /purchase/%s", item_id)
    if not item_id.isdigit():
        logger.info("Failure: invalid item_id '%s'", item_id)
        return jsonify({"message": "Invalid item_id"}), 400

    item_id_int = int(item_id)
    status_code, item = get_item_info(CATALOG_SERVICE_URL, item_id)
    if status_code == 404:
        logger.info("Failure: item_id %s not found in catalog", item_id)
        return jsonify({"message": f"Item not found: {item_id}"}), 404
    if status_code != 200:
        logger.info("Failure: catalog info request returned status %s", status_code)
        return jsonify({"message": "Catalog service error"}), 500

    quantity = item.get("quantity", 0)
    if quantity <= 0:
        logger.info("Out-of-stock result for item_id %s", item_id)
        return jsonify({"message": "Item out of stock", "item_id": item_id_int}), 409

    new_quantity = quantity - 1
    update_status, update_body = update_item_quantity(
        CATALOG_SERVICE_URL,
        item_id,
        new_quantity,
    )
    if update_status != 200:
        logger.info(
            "Failure: catalog quantity decrement failed for item_id %s with status %s",
            item_id,
            update_status,
        )
        return jsonify({"message": "Catalog service error"}), 500

    logger.info("Successful quantity decrement for item_id %s", item_id)
    log_purchase(item_id_int, item["title"], item["price"])
    logger.info("Order log write completed for item_id %s", item_id)
    return jsonify({"message": "Purchase successful", "item_id": item_id_int}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
