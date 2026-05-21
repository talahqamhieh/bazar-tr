"""Forward client requests to catalog or order replicas via urllib."""

import json
import logging
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)


def forward_request(method, url, body=None):
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
        return error.code, json.loads(payload) if payload else {"message": "Backend request failed"}
    except urllib.error.URLError as error:
        logger.info("Backend unavailable: %s", error)
        return 500, {"message": "Backend service unavailable"}
