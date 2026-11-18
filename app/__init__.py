import logging
import os

from flask import Flask
from jinja2 import ChoiceLoader, PackageLoader

from app.lib.context_processor import now_iso_8601
from app.lib.talisman import talisman
from app.lib.template_filters import slugify


def create_app(config_class):
    app = Flask(__name__, static_url_path="/static")
    app.config.from_object(config_class)

    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(
        gunicorn_error_logger.level or os.getenv("LOG_LEVEL", "warning").upper()
    )

    proxy_depth = app.config["PROXY_DEPTH"]
    if proxy_depth:
        from werkzeug.middleware.proxy_fix import ProxyFix

        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_host=proxy_depth,
            x_proto=proxy_depth,
            x_for=proxy_depth,
            x_prefix=proxy_depth,
        )

    talisman.init_app(
        app,
        content_security_policy=app.config["CONTENT_SECURITY_POLICY"],
        allow_google_content_security_policy=True,
        force_https=app.config["FORCE_HTTPS"],
    )

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.autoescape = True
    app.jinja_env.loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PackageLoader("tna_frontend_jinja"),
        ]
    )

    @app.context_processor
    def context_processor():
        return {
            "app_config": {
                "ENVIRONMENT_NAME": app.config["ENVIRONMENT_NAME"],
                "CONTAINER_IMAGE": app.config["CONTAINER_IMAGE"],
                "BUILD_VERSION": app.config["BUILD_VERSION"],
                "TNA_FRONTEND_VERSION": app.config["TNA_FRONTEND_VERSION"],
                "COOKIE_DOMAIN": app.config["COOKIE_DOMAIN"],
                "COOKIE_PREFERENCES_URL": app.config["COOKIE_PREFERENCES_URL"],
                "GA4_ID": app.config["GA4_ID"],
            },
            "feature": {},
            "now_iso_8601": now_iso_8601,
        }

    app.add_template_filter(slugify)

    from .healthcheck import bp as healthcheck_bp
    from .main import bp as site_bp

    app.register_blueprint(healthcheck_bp, url_prefix="/healthcheck")
    app.register_blueprint(site_bp)

    return app
