import logging

from flask import Flask, jsonify, request

from db import get_book_by_id, search_books_by_topic, update_book_by_id
from config import DB_PATH, PORT, SERVICE_NAME

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Not found"}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"message": "Bad request"}), 400


@app.get("/search/<topic>")
def search(topic):
    logger.info("[%s] Incoming request: GET /search/%s", SERVICE_NAME, topic)
    books = search_books_by_topic(topic)
    if not books:
        # Unknown topics return 404 JSON instead of an empty list.
        logger.info("Failure: no books found for topic '%s'", topic)
        return jsonify({"message": f"No books found for topic: {topic}"}), 404
    logger.info("Success: found %d book(s) for topic '%s'", len(books), topic)
    return jsonify(books), 200


@app.get("/info/<item_id>")
def info(item_id):
    logger.info("[%s] Incoming request: GET /info/%s", SERVICE_NAME, item_id)
    if not item_id.isdigit():
        logger.info("Failure: invalid item_id '%s'", item_id)
        return jsonify({"message": "Invalid item_id"}), 400

    book = get_book_by_id(int(item_id))
    if book is None:
        logger.info("Failure: item_id %s not found", item_id)
        return jsonify({"message": f"Item not found: {item_id}"}), 404

    logger.info("Success: returned info for item_id %s", item_id)
    return jsonify(book), 200


def _is_non_negative_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


@app.put("/update/<item_id>")
def update(item_id):
    logger.info("[%s] Incoming request: PUT /update/%s", SERVICE_NAME, item_id)
    if not item_id.isdigit():
        logger.info("Validation failure: invalid item_id '%s'", item_id)
        return jsonify({"message": "Invalid item_id"}), 400

    payload = request.get_json(silent=True)
    if not payload:
        logger.info("Validation failure: missing or empty request body")
        return jsonify({"message": "Request body is required"}), 400

    has_price = "price" in payload
    has_quantity = "quantity" in payload
    if not has_price and not has_quantity:
        logger.info("Validation failure: neither price nor quantity provided")
        return jsonify({"message": "At least one of price or quantity is required"}), 400

    price = quantity = None
    if has_price:
        price = payload["price"]
        if not _is_non_negative_int(price):
            logger.info("Validation failure: invalid price for item_id %s", item_id)
            return jsonify({"message": "price must be a non-negative integer"}), 400
    if has_quantity:
        quantity = payload["quantity"]
        if not _is_non_negative_int(quantity):
            logger.info("Validation failure: invalid quantity for item_id %s", item_id)
            return jsonify({"message": "quantity must be a non-negative integer"}), 400

    book = update_book_by_id(int(item_id), price=price, quantity=quantity)
    if book is None:
        logger.info("Item not found: item_id %s", item_id)
        return jsonify({"message": f"Item not found: {item_id}"}), 404

    logger.info("Success: updated item_id %s", item_id)
    return jsonify({"message": "Item updated successfully", "item": book}), 200


if __name__ == "__main__":
    logger.info("Starting %s on port %s with database %s", SERVICE_NAME, PORT, DB_PATH)
    app.run(host="0.0.0.0", port=PORT)
