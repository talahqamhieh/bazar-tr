"""HTTP helpers for catalog reads/updates and front-end cache invalidation."""

import json
import logging
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)


def _request_json(method, url, body=None):
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            payload = response.read().decode()
            return response.status, json.loads(payload) if payload else {}
    except urllib.error.HTTPError as error:
        payload = error.read().decode()
        return error.code, json.loads(payload) if payload else {"message": "Catalog request failed"}
    except urllib.error.URLError as error:
        logger.info("Catalog request failure: %s", error)
        return 500, {"message": "Catalog service unavailable"}


def get_item_info(base_url, item_id):
    url = f"{base_url.rstrip('/')}/info/{item_id}"
    logger.info("Catalog info request: GET %s", url)
    return _request_json("GET", url)


def update_item_quantity(base_url, item_id, quantity):
    url = f"{base_url.rstrip('/')}/update/{item_id}"
    logger.info("Catalog update request: PUT %s quantity=%s", url, quantity)
    return _request_json("PUT", url, {"quantity": quantity})


def invalidate_frontend_cache(base_url, item_id):
    url = f"{base_url.rstrip('/')}/internal/invalidate/{item_id}"
    logger.info("Frontend invalidation request: POST %s", url)
    return _request_json("POST", url)
