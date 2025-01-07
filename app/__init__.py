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
        },
    )

    csp_self = "'self'"
    csp_none = "'none'"
    talisman.init_app(
        app,
        content_security_policy={
            "default-src": csp_self,
            "base-uri": csp_none,
            "object-src": csp_none,
            **(
                {"img-src": app.config.get("CSP_IMG_SRC")}
                if app.config.get("CSP_IMG_SRC") != csp_self
                else {}
            ),
            **(
                {"script-src": app.config.get("CSP_SCRIPT_SRC")}
                if app.config.get("CSP_SCRIPT_SRC") != csp_self
                else {}
            ),
            **(
                {"script-src-elem": app.config.get("CSP_SCRIPT_SRC_ELEM")}
                if app.config.get("CSP_SCRIPT_SRC_ELEM") != csp_self
                else {}
            ),
            **(
                {"style-src": app.config.get("CSP_STYLE_SRC")}
                if app.config.get("CSP_STYLE_SRC") != csp_self
                else {}
            ),
            **(
                {"font-src": app.config.get("CSP_FONT_SRC")}
                if app.config.get("CSP_FONT_SRC") != csp_self
                else {}
            ),
            **(
                {"connect-src": app.config.get("CSP_CONNECT_SRC")}
                if app.config.get("CSP_CONNECT_SRC") != csp_self
                else {}
            ),
            **(
                {"media-src": app.config.get("CSP_MEDIA_SRC")}
                if app.config.get("CSP_MEDIA_SRC") != csp_self
                else {}
            ),
            **(
                {"worker-src": app.config.get("CSP_WORKER_SRC")}
                if app.config.get("CSP_WORKER_SRC") != csp_self
                else {}
            ),
            **(
                {"frame-src": app.config.get("CSP_FRAME_SRC")}
                if app.config.get("CSP_FRAME_SRC") != csp_self
                else {}
            ),
        },
        # content_security_policy_nonce_in=["script-src", "style-src"],
        feature_policy={
            "camera": csp_none,
            "fullscreen": app.config.get("CSP_FEATURE_FULLSCREEN") or csp_self,
            "geolocation": csp_none,
            "microphone": csp_none,
            "screen-wake-lock": csp_none,
        },
        force_https=app.config["FORCE_HTTPS"],
    )

    @app.after_request
    def apply_extra_headers(response):
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
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
