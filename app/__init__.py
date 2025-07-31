import logging

from app.lib.cache import cache
from app.lib.context_processor import cookie_preference, now_iso_8601
from app.lib.talisman import talisman
from app.lib.template_filters import slugify
from flask import Flask
from jinja2 import ChoiceLoader, PackageLoader


def create_app(config_class):
    app = Flask(__name__, static_url_path="/static")
    app.config.from_object(config_class)

    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(gunicorn_error_logger.level or "DEBUG")

    cache.init_app(
        app,
        config={
            "CACHE_TYPE": app.config.get("CACHE_TYPE"),
            "CACHE_DEFAULT_TIMEOUT": app.config.get("CACHE_DEFAULT_TIMEOUT"),
            "CACHE_IGNORE_ERRORS": app.config.get("CACHE_IGNORE_ERRORS"),
            "CACHE_DIR": app.config.get("CACHE_DIR"),
            "CACHE_REDIS_URL": app.config.get("CACHE_REDIS_URL"),
        },
    )

    csp_self = "'self'"
    csp_none = "'none'"
    default_csp = csp_self
    csp_rules = {
        key.replace("_", "-"): value
        for key, value in app.config.get_namespace(
            "CSP_", lowercase=True, trim_namespace=True
        ).items()
        if not key.startswith("feature_") and value not in [None, [default_csp]]
    }
    talisman.init_app(
        app,
        content_security_policy={
            "default-src": default_csp,
            "base-uri": csp_none,
            "object-src": csp_none,
        }
        | csp_rules,
        feature_policy={
            "fullscreen": app.config.get("CSP_FEATURE_FULLSCREEN", csp_self),
            "picture-in-picture": app.config.get(
                "CSP_FEATURE_PICTURE_IN_PICTURE", csp_self
            ),
        },
        force_https=app.config["FORCE_HTTPS"],
    )

    @app.after_request
    def apply_extra_headers(response):
        if "X-Permitted-Cross-Domain-Policies" not in response.headers:
            response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        if "Cross-Origin-Embedder-Policy" not in response.headers:
            response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"
        if "Cross-Origin-Opener-Policy" not in response.headers:
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        if "Cross-Origin-Resource-Policy" not in response.headers:
            response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        return response

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PackageLoader("tna_frontend_jinja"),
        ]
    )

    app.add_template_filter(slugify)

    @app.context_processor
    def context_processor():
        return dict(
            cookie_preference=cookie_preference,
            now_iso_8601=now_iso_8601,
            app_config={
                "ENVIRONMENT_NAME": app.config.get("ENVIRONMENT_NAME"),
                "TNA_FRONTEND_VERSION": app.config.get("TNA_FRONTEND_VERSION"),
                "BUILD_VERSION": app.config.get("BUILD_VERSION"),
                "COOKIE_DOMAIN": app.config.get("COOKIE_DOMAIN"),
                "GA4_ID": app.config.get("GA4_ID"),
            },
            feature={},
        )

    from .healthcheck import bp as healthcheck_bp
    from .main import bp as site_bp

    app.register_blueprint(site_bp)
    app.register_blueprint(healthcheck_bp, url_prefix="/healthcheck")

    return app
