"""Replicate a successful purchase row to the peer order service."""

import json
import logging
import urllib.error
import urllib.request

from config import ORDER_PEER_URL

logger = logging.getLogger(__name__)


def sync_order_to_peer(order_row):
    if not ORDER_PEER_URL:
        logger.info(
            "No order peer URL configured; skipping sync for item_id %s",
            order_row["item_id"],
        )
        return True

    url = f"{ORDER_PEER_URL.rstrip('/')}/internal/sync_order"
    data = json.dumps(order_row).encode()
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
