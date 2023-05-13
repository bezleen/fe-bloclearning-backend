# -*- coding: utf-8 -*-

import os
import logging
import logging.config
from flask import Flask, request, jsonify, current_app
from src.flask_secure import SecureFlask
from flask_cors import CORS


from .config import DefaultConfig, LoggingConfig
from .extensions import (
    mdb, redis_cached
)

# For import *
__all__ = ['create_app']


def create_app(config=None, app_name=None):
    """Create a Flask app."""
    if app_name is None:
        app_name = DefaultConfig.PROJECT

    app = SecureFlask(app_name, instance_relative_config=True,
                      md5_endpoints=DefaultConfig.MD5_ENDPOINTS)
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.static_url_path = ''
    app.static_folder = 'src/static'
    configure_app(app, config)
    configure_extensions(app)
    configure_blueprints(app)
    configure_template_filters(app)
    configure_error_handlers(app)
    configure_logging_level(app)

    return app


def configure_app(app, config=None):
    app.config.from_object(DefaultConfig)
    if config:
        app.config.from_object(config)


def configure_extensions(app):

    # redis cache
    redis_cached.init_app(app, config_prefix="REDIS_CACHED")

    # mdb
    mdb.init_app(app, uri=app.config['MONGO_URI'])

    logging.config.dictConfig(LoggingConfig.LOGGING_CONFIG)


def configure_blueprints(app):
    """Configure blueprints in views."""
    from src.api import DEFAULT_BLUEPRINTS

    for blueprint in DEFAULT_BLUEPRINTS:
        app.register_blueprint(blueprint)


def configure_template_filters(app):
    @app.template_filter()
    def pretty_date(value):
        return pretty_date(value)

    @app.template_filter()
    def format_date(value, format='%Y-%m-%d'):
        return value.strftime(format)


def configure_logging_level(app):
    app.logger.setLevel(logging.DEBUG)


def configure_error_handlers(app):

    @app.errorhandler(403)
    def forbidden_page(error):
        return jsonify(msg="forbidden"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify(msg="notfound"), 404

    @app.errorhandler(Exception)
    def server_error(e):
        app.logger.exception(e)
        return jsonify(msg="server_error", code=500), 500
