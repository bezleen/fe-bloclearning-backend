# -*- coding: utf-8 -*-

from flask_redis import Redis
import redis
from flask_pymongo import PyMongo

from .config import DefaultConfig as Conf
import src.constants as Consts


mdb = PyMongo()
redis_cached = Redis(config_prefix="REDIS_CACHED")
