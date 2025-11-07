import json
import os

from app.lib.util import strtobool


class Features:
    pass


class Production(Features):
    ENVIRONMENT_NAME: str = os.environ.get("ENVIRONMENT_NAME", "production")
    CONTAINER_IMAGE: str = os.environ.get("CONTAINER_IMAGE", "")
    BUILD_VERSION: str = os.environ.get("BUILD_VERSION", "")
    TNA_FRONTEND_VERSION: str = ""
    try:
        with open(
            os.path.join(
                os.path.realpath(os.path.dirname(__file__)),
                "node_modules/@nationalarchives/frontend",
                "package.json",
            )
        ) as package_json:
            try:
                data = json.load(package_json)
                TNA_FRONTEND_VERSION = data["version"] or ""
            except ValueError:
                pass
    except FileNotFoundError:
        pass

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")

    DEBUG: bool = strtobool(os.getenv("DEBUG", "False"))

    COOKIE_DOMAIN: str = os.environ.get("COOKIE_DOMAIN", "")

    CSP_IMG_SRC: list[str] = os.environ.get("CSP_IMG_SRC", "'self'").split(",")
    CSP_SCRIPT_SRC: list[str] = os.environ.get("CSP_SCRIPT_SRC", "'self'").split(",")
    CSP_STYLE_SRC: list[str] = os.environ.get("CSP_STYLE_SRC", "'self'").split(",")
    CSP_FONT_SRC: list[str] = os.environ.get("CSP_FONT_SRC", "'self'").split(",")
    CSP_CONNECT_SRC: list[str] = os.environ.get("CSP_CONNECT_SRC", "'self'").split(",")
    CSP_MEDIA_SRC: list[str] = os.environ.get("CSP_MEDIA_SRC", "'self'").split(",")
    CSP_WORKER_SRC: list[str] = os.environ.get("CSP_WORKER_SRC", "'self'").split(",")
    CSP_FRAME_SRC: list[str] = os.environ.get("CSP_FRAME_SRC", "'self'").split(",")
    CSP_FRAME_ANCESTORS: list[str] = os.environ.get(
        "CSP_FRAME_ANCESTORS", "'self'"
    ).split(",")
    CSP_FEATURE_FULLSCREEN: list[str] = os.environ.get(
        "CSP_FEATURE_FULLSCREEN", "'self'"
    ).split(",")
    CSP_FEATURE_PICTURE_IN_PICTURE: list[str] = os.environ.get(
        "CSP_FEATURE_PICTURE_IN_PICTURE", "'self'"
    ).split(",")
    CSP_REPORT_URL: str = os.environ.get("CSP_REPORT_URL", "")
    if CSP_REPORT_URL:
        CSP_REPORT_URL += f"&sentry_release={BUILD_VERSION}" if BUILD_VERSION else ""
    FORCE_HTTPS: bool = strtobool(os.getenv("FORCE_HTTPS", "True"))
    PREFERRED_URL_SCHEME: str = os.getenv("PREFERRED_URL_SCHEME", "https")

    CACHE_TYPE: str = "FileSystemCache"
    CACHE_DEFAULT_TIMEOUT: int = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", "900"))
    CACHE_IGNORE_ERRORS: bool = True
    CACHE_DIR: str = os.environ.get("CACHE_DIR", "/tmp")
    CACHE_REDIS_URL: str = os.environ.get("CACHE_REDIS_URL", "")

    GA4_ID: str = os.environ.get("GA4_ID", "")


class Staging(Production):
    CACHE_DEFAULT_TIMEOUT: int = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", "60"))


class Develop(Production):
    CACHE_DEFAULT_TIMEOUT: int = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", "1"))


class Test(Production):
    ENVIRONMENT_NAME: str = "test"

    SECRET_KEY: str = "abc123"
    DEBUG: bool = True
    TESTING: bool = True
    EXPLAIN_TEMPLATE_LOADING: bool = True

    CACHE_TYPE: str = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT: int = 1

    FORCE_HTTPS: bool = False
    PREFERRED_URL_SCHEME: str = "http"
