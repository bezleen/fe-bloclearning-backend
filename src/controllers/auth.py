import datetime as dt
import traceback

import names
import jwt
from bson.objectid import ObjectId
import pydash as py_


import src.functions as funcs
import src.models.repo as Repo
import src.enums as Enums
import src.constants as Consts
from src.config import DefaultConfig as Conf
from src.utils.util_datetime import tzware_datetime, tzware_timestamp


class Authentication(object):

    @classmethod
    def authenticate_wallet_server_side(cls, signature, public_key, timestamp, address):
        server_time = tzware_datetime()
        custom_id = cls.verify_signature(signature, public_key, timestamp, address)
        if not custom_id:
            return
        custom_id_hash = funcs.ora_hash(custom_id)
        user_obj = Repo.mUser.get_item_with({"custom_id": custom_id_hash})
        user_obj = None

        if not user_obj:
            user_id = ObjectId()
            name = names.get_first_name()
            name_idx = funcs.safe_string(name)
            access_token = cls.generate_access_token(str(user_id), is_refresh_token=False)
            refresh_token = cls.generate_access_token(str(user_id), is_refresh_token=True)
            Repo.mUser.insert({
                "_id": user_id,
                "custom_id": custom_id_hash,
                "name_idx": name_idx,
                "internal": {
                    "last_access_token": access_token,
                    "last_login": server_time,
                },
                "read_only": {
                    "name": name,
                    "role": Enums.UserRole.DAO_MEMBER
                }
            })
        else:
            user_id = py_.get(user_obj, '_id')
            access_token = cls.generate_access_token(str(user_id), is_refresh_token=False)
            refresh_token = cls.generate_access_token(str(user_id), is_refresh_token=True)

        user_id = py_.to_string(user_id)
        response = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "_id": user_id,
            "server_time": int(server_time.timestamp())
        }
        return response

    @classmethod
    def generate_access_token(cls, user_id, is_refresh_token=False):
        if not user_id:
            return None

        server_time = tzware_datetime()

        exp_at = dt.timedelta(seconds=Consts.ACCESS_TOKEN_TTL) + server_time
        exp_at_ts = int(exp_at.timestamp())
        is_access_token = 1

        if is_refresh_token:
            exp_at = dt.timedelta(seconds=Consts.REFRESH_TOKEN_TTL) + server_time
            exp_at_ts = int(exp_at.timestamp())
            is_access_token = 0

        payload_jwt = {
            "iss": 'ora-sci',
            "exp": exp_at_ts,
            "iat": tzware_timestamp(),
            "app_id": "coup",
            "_id": user_id,
            "access_token": is_access_token
        }
        token = cls.generate_jwt_token(payload_jwt)
        return token

    @classmethod
    def generate_jwt_token(cls, payload):
        encoded = jwt.encode(payload, Conf.SECRET_KEY, algorithm="HS256")
        return encoded

    @classmethod
    def decode_jwt(self, token, options={}):
        try:
            payload = jwt.decode(token, Conf.SECRET_KEY, ["HS256"], options=options)
            return payload
        except:
            traceback.print_exc()
            return None

    @classmethod
    def verify_signature(cls, signature, public_key, timestamp, address):
        # TODO: verify signature
        return address
