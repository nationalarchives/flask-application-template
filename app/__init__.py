import logging

from app.lib import cache
from app.lib.context_processor import (
    cookie_preference,
    merge_dict,
    merge_dict_if,
    now_iso_8601,
)
from app.lib.template_filters import slugify
from flask import Flask
from flask_talisman import Talisman
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
            "CACHE_TYPE": app.config["CACHE_TYPE"],
            "CACHE_DEFAULT_TIMEOUT": app.config["CACHE_DEFAULT_TIMEOUT"],
            "CACHE_IGNORE_ERRORS": app.config["CACHE_IGNORE_ERRORS"],
            "CACHE_DIR": app.config["CACHE_DIR"],
        },
    )

    csp_self = "'self'"
    csp_none = "'none'"
    Talisman(
        app,
        content_security_policy={
            "default-src": csp_self,
            "base-uri": csp_none,
            "object-src": csp_none,
            **(
                {"img-src": app.config["CSP_IMG_SRC"]}
                if app.config["CSP_IMG_SRC"] != csp_self
                else {}
            ),
            **(
                {"script-src": app.config["CSP_SCRIPT_SRC"]}
                if app.config["CSP_SCRIPT_SRC"] != csp_self
                else {}
            ),
            **(
                {"script-src-elem": app.config["CSP_SCRIPT_SRC_ELEM"]}
                if app.config["CSP_SCRIPT_SRC_ELEM"] != csp_self
                else {}
            ),
            **(
                {"style-src": app.config["CSP_STYLE_SRC"]}
                if app.config["CSP_STYLE_SRC"] != csp_self
                else {}
            ),
            **(
                {"font-src": app.config["CSP_FONT_SRC"]}
                if app.config["CSP_FONT_SRC"] != csp_self
                else {}
            ),
            **(
                {"connect-src": app.config["CSP_CONNECT_SRC"]}
                if app.config["CSP_CONNECT_SRC"] != csp_self
                else {}
            ),
            **(
                {"media-src": app.config["CSP_MEDIA_SRC"]}
                if app.config["CSP_MEDIA_SRC"] != csp_self
                else {}
            ),
            **(
                {"worker-src": app.config["CSP_WORKER_SRC"]}
                if app.config["CSP_WORKER_SRC"] != csp_self
                else {}
            ),
            **(
                {"frame-src": app.config["CSP_FRAME_SRC"]}
                if app.config["CSP_FRAME_SRC"] != csp_self
                else {}
            ),
        },
        # content_security_policy_nonce_in=["script-src", "style-src"],
        feature_policy={
            "camera": csp_none,
            "fullscreen": csp_self,
            "geolocation": csp_none,
            "microphone": csp_none,
            "screen-wake-lock": csp_none,
        },
        force_https=app.config["FORCE_HTTPS"],
        frame_options="ALLOW-FROM",
        frame_options_allow_from=app.config["FRAME_DOMAIN_ALLOW"],
    )

    @app.after_request
    def apply_extra_headers(response):
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Embedder-Policy"] = "credentialless"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Cache-Control"] = (
            f"public, max-age={app.config['CACHE_HEADER_DURATION']}"
        )
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
            merge_dict=merge_dict,
            merge_dict_if=merge_dict_if,
            cookie_preference=cookie_preference,
            now_iso_8601=now_iso_8601,
            app_config=app.config,
        )

    from .healthcheck import bp as healthcheck_bp
    from .main import bp as site_bp

    app.register_blueprint(site_bp)
    app.register_blueprint(healthcheck_bp, url_prefix="/healthcheck")

    return app
