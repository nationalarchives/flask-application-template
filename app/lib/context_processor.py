import json
from datetime import datetime
from urllib.parse import unquote

from flask import request


def merge_dict(dict, new_data):
    return dict | new_data


def merge_dict_if(dict, new_data, condition):
    return dict | new_data if condition else dict


def now_iso_8601():
    now = datetime.now()
    now_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return now_date


def cookie_preference(policy):
    if "cookies_policy" in request.cookies:
        cookies_policy = request.cookies["cookies_policy"]
        preferences = json.loads(unquote(cookies_policy))
        return preferences[policy] if policy in preferences else None
    return None
