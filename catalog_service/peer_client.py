import json
import logging
import urllib.error
import urllib.request

from config import CATALOG_PEER_URL

logger = logging.getLogger(__name__)


def sync_update_to_peer(item_id, price, quantity):
    if not CATALOG_PEER_URL:
        logger.info("No catalog peer URL configured; skipping sync for item_id %s", item_id)
        return True

    url = f"{CATALOG_PEER_URL.rstrip('/')}/internal/sync_update/{item_id}"
    body = {}
    if price is not None:
        body["price"] = price
    if quantity is not None:
        body["quantity"] = quantity

    data = json.dumps(body).encode()
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    logger.info("Sync request sent to peer: POST %s", url)
    try:
        with urllib.request.urlopen(request) as response:
            return response.status == 200
    except urllib.error.HTTPError as error:
        logger.info("Sync failure: peer returned status %s", error.code)
        return False
    except urllib.error.URLError as error:
        logger.info("Sync failure: peer unavailable (%s)", error)
        return False
