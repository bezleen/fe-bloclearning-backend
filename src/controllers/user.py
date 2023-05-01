import datetime
from dateutil.relativedelta import relativedelta
from bson.objectid import ObjectId
import pytz
import pydash as py_
from operator import itemgetter

import src.enums as Enums
from src.extensions import redis_cached
import src.controllers as Controllers
import src.constants as Consts
import src.models.repo as Repo
import json
from bson import json_util


class User(object):

    @classmethod
    def check_conflict_token(cls, user_id, access_token):

        return False
