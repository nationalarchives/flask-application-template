from flask import request
from flask_caching import Cache

cache = Cache()


def cache_key_prefix():
    """Make a key that includes GET parameters."""
    theme = request.cookies.get("theme", "")
    return f"{request.full_path}{theme if theme in ['system', 'light', 'dark'] else ''}"
