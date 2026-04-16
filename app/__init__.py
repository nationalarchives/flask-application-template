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
    app.logger.setLevel(gunicorn_error_logger.level or "WARNING")

    cache.init_app(
        app,
        config={
            "CACHE_TYPE": app.config["CACHE_TYPE"],
            "CACHE_DEFAULT_TIMEOUT": app.config["CACHE_DEFAULT_TIMEOUT"],
            "CACHE_IGNORE_ERRORS": app.config["CACHE_IGNORE_ERRORS"],
            "CACHE_DIR": app.config["CACHE_DIR"],
            "CACHE_REDIS_URL": app.config["CACHE_REDIS_URL"],
        },
    )

    talisman.init_app(
        app,
        content_security_policy=app.config["CONTENT_SECURITY_POLICY"],
        allow_google_content_security_policy=True,
        force_https=app.config["FORCE_HTTPS"],
    )

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PackageLoader("tna_frontend_jinja"),
        ]
    )

    @app.context_processor
    def context_processor():
        return dict(
            cookie_preference=cookie_preference,
            now_iso_8601=now_iso_8601,
            app_config={
                "ENVIRONMENT_NAME": app.config["ENVIRONMENT_NAME"],
                "CONTAINER_IMAGE": app.config["CONTAINER_IMAGE"],
                "BUILD_VERSION": app.config["BUILD_VERSION"],
                "TNA_FRONTEND_VERSION": app.config["TNA_FRONTEND_VERSION"],
                "COOKIE_DOMAIN": app.config["COOKIE_DOMAIN"],
                "COOKIE_PREFERENCES_URL": app.config["COOKIE_PREFERENCES_URL"],
                "GA4_ID": app.config["GA4_ID"],
            },
            feature={},
        )

    app.add_template_filter(slugify)

    from .healthcheck import bp as healthcheck_bp
    from .main import bp as site_bp

    app.register_blueprint(healthcheck_bp, url_prefix="/healthcheck")
    app.register_blueprint(site_bp)

    return app
