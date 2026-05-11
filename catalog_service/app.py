import logging

from flask import Flask, jsonify

from db import get_book_by_id, search_books_by_topic

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
    logger.info("Incoming request: GET /search/%s", topic)
    books = search_books_by_topic(topic)
    if not books:
        # Unknown topics return 404 JSON instead of an empty list.
        logger.info("Failure: no books found for topic '%s'", topic)
        return jsonify({"message": f"No books found for topic: {topic}"}), 404
    logger.info("Success: found %d book(s) for topic '%s'", len(books), topic)
    return jsonify(books), 200


@app.get("/info/<item_id>")
def info(item_id):
    logger.info("Incoming request: GET /info/%s", item_id)
    if not item_id.isdigit():
        logger.info("Failure: invalid item_id '%s'", item_id)
        return jsonify({"message": "Invalid item_id"}), 400

    book = get_book_by_id(int(item_id))
    if book is None:
        logger.info("Failure: item_id %s not found", item_id)
        return jsonify({"message": f"Item not found: {item_id}"}), 404

    logger.info("Success: returned info for item_id %s", item_id)
    return jsonify(book), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
