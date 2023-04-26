# -*- coding: utf-8 -*-
import os
import logging
import pydash as py_
from dotenv import load_dotenv

load_dotenv()


# create log dir
BASE_DIR = os.path.abspath(os.curdir)
# BASE_DIR = "/var/log/apps/"

# Create log folder
log_dir = os.path.join(BASE_DIR, 'logging')
if not os.path.exists(log_dir):
    print(f"--- {log_dir} created ---")
    os.mkdir(log_dir)


class BaseConfig(object):
    PROJECT = "Ora-Sci"

    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    DEBUG = False
    TESTING = False

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = os.getenv("SECRET_KEY")


class DefaultConfig(BaseConfig):
    DEBUG = True

    ACCEPT_LANGUAGES = ['vi']
    BABEL_DEFAULT_LOCALE = 'en'
    MONGO_URI = os.getenv('MONGO_URI', '')

    REDIS_CACHED_URL = os.getenv('REDIS_CACHED_URL')
    REDIS_CACHED_DECODE_RESPONSES = True

    SECRET_KEY = os.getenv('JWT_SECRET')

    LOGGING_LEVEL = logging.DEBUG
    LOGGING_CONFIG_FILE = os.path.join(BASE_DIR, 'logging.conf')

    DEVELOP = os.getenv("DEVELOP", 0) or 0

    SECURE_PAYLOAD_ENDPOINT = [
    ]

    MD5_ENDPOINTS = [
    ]


class LoggingConfig(BaseConfig):
    # Config log
    LOGGING_CONFIG = {
        'version': 1,
        'formatters': {
            'defaultColored': {
                # '()': 'colorlog.ColoredFormatter',
                'format': '[%(asctime)s] -%(levelname)8s - %(module)10s - %(funcName)s: %(message)s'
            },
            'default': {
                'format': '[%(asctime)s] -%(levelname)8s - %(module)10s - %(funcName)s: %(message)s'
            },
            'full': {
                'format': '[%(asctime)s] - %(levelname)s - %(module)s - [in %(pathname)s:%(lineno)d]\t: %(message)s',
            }
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'default',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'logging', 'app.log'),
                'maxBytes': 5000000,
                'backupCount': 10
            },
            'debug': {
                'level': 'DEBUG',
                'formatter': 'default',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'logging', 'app.debug.log'),
                'maxBytes': 5000000,
                'backupCount': 10
            },
            'error': {
                'level': 'ERROR',
                'formatter': 'full',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'logging', 'app.error.log'),
                'maxBytes': 5000000,
                'backupCount': 10
            },
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'defaultColored'
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['default', 'debug', 'error', 'console']
        }
    }
