import logging

from flask import Flask, jsonify, request

from client import get_item_info, invalidate_frontend_cache, update_item_quantity
from config import (
    CATALOG_SERVICE_URL,
    DB_PATH,
    FRONTEND_INVALIDATION_URL,
    ORDER_PEER_URL,
    PORT,
    SERVICE_NAME,
)
from db import init_db, log_purchase, save_synced_order
from peer_client import sync_order_to_peer

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


@app.get("/")
def home():
    return jsonify({"service": SERVICE_NAME, "status": "running"}), 200


@app.get("/health")
def health():
    return jsonify({"service": SERVICE_NAME, "status": "ok"}), 200


@app.post("/purchase/<item_id>")
def purchase(item_id):
    logger.info("[%s] Incoming request: POST /purchase/%s", SERVICE_NAME, item_id)
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
    invalidate_status, _ = invalidate_frontend_cache(
        FRONTEND_INVALIDATION_URL,
        item_id,
    )
    if invalidate_status == 200:
        logger.info("Cache invalidation completed for item_id %s", item_id)
    else:
        logger.info(
            "Cache invalidation failed for item_id %s with status %s; continuing purchase",
            item_id,
            invalidate_status,
        )

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
    logger.info("Local successful purchase for item_id %s", item_id)
    order_row = log_purchase(item_id_int, item["title"], item["price"])
    logger.info("Local order row written for item_id %s", item_id)

    if not sync_order_to_peer(order_row):
        logger.info(
            "Sync failure after local order log for item_id %s; returning local success",
            item_id,
        )

    return jsonify({"message": "Purchase successful", "item_id": item_id_int}), 201


@app.post("/internal/sync_order")
def sync_order():
    logger.info("[%s] Sync request received from peer: POST /internal/sync_order", SERVICE_NAME)
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"message": "Request body is required"}), 400

    required_fields = ("item_id", "title", "price_at_purchase", "purchased_at")
    missing = [field for field in required_fields if field not in payload]
    if missing:
        return jsonify({"message": f"Missing fields: {', '.join(missing)}"}), 400

    save_synced_order(
        payload["item_id"],
        payload["title"],
        payload["price_at_purchase"],
        payload["purchased_at"],
    )
    logger.info("Synced order row written successfully for item_id %s", payload["item_id"])
    return jsonify({"message": "Order sync applied", "item_id": payload["item_id"]}), 200


if __name__ == "__main__":
    logger.info(
        "Starting %s on port %s with database %s, catalog %s, peer %s",
        SERVICE_NAME,
        PORT,
        DB_PATH,
        CATALOG_SERVICE_URL,
        ORDER_PEER_URL or "none",
    )
    app.run(host="0.0.0.0", port=PORT)
