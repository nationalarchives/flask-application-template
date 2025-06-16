from flask import request
from flask_caching import Cache

cache = Cache()


def cache_key_prefix():
    """Make a key that includes GET parameters."""
    return f"{request.full_path}{request.cookies.get('cookie_preferences_set' or '')}{request.cookies.get('theme' or '')}"
