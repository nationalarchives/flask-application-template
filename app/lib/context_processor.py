import json
from datetime import datetime, timezone
from urllib.parse import unquote

from flask import request


def now_iso_8601():
    now = datetime.now(tz=timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")


def cookie_preference(policy):
    if "cookie_preferences" in request.cookies:
        cookie_preferences = request.cookies["cookie_preferences"]
        preferences = json.loads(unquote(cookie_preferences))
        return preferences.get(policy, None)
    return None
