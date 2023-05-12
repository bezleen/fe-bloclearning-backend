import random
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
from src.extensions import redis_cached


class Authentication(object):

    @classmethod
    def authenticate_wallet_server_side(cls, signature, public_key, timestamp, address):
        server_time = tzware_datetime()
        custom_id = cls.verify_signature(
            signature, public_key, timestamp, address)
        if not custom_id:
            return
        custom_id_hash = funcs.ora_hash(custom_id)
        user_obj = Repo.mUser.get_item_with({"custom_id": custom_id_hash})

        if not user_obj:
            user_id = ObjectId()
            name = names.get_first_name()
            name_idx = funcs.safe_string(name)
            access_token = cls.generate_access_token(
                str(user_id), Consts.DEFAULT_ROLE_OBJ, is_refresh_token=False)
            refresh_token = cls.generate_access_token(
                str(user_id), Consts.DEFAULT_ROLE_OBJ, is_refresh_token=True)
            avatar = random.choice(Enums.Avatar.list())
            Repo.mUser.insert({
                "_id": user_id,
                "custom_id": custom_id_hash,
                "name_idx": name_idx,
                "internal": {
                    "last_access_token": access_token,
                    "last_login": int(server_time.timestamp()),
                },
                "read_only": {
                    "name": name,
                    "role": Consts.DEFAULT_ROLE_OBJ,
                    "avatar": avatar
                }
            })
            cls.sync_token(user_id, access_token)
        else:

            user_id = py_.get(user_obj, '_id')
            user_role = py_.get(user_obj, "read_only.role")
            access_token = cls.generate_access_token(
                str(user_id), user_role, is_refresh_token=False)
            refresh_token = cls.generate_access_token(
                str(user_id), user_role, is_refresh_token=True)
            cls.sync_token(user_id, access_token)

        user_id = py_.to_string(user_id)
        response = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "_id": user_id,
            "server_time": int(server_time.timestamp())
        }
        return response

    @ classmethod
    def generate_access_token(cls, user_id, role, is_refresh_token=False):
        if not user_id:
            return None

        server_time = tzware_datetime()

        exp_at = dt.timedelta(seconds=Consts.ACCESS_TOKEN_TTL) + server_time
        exp_at_ts = int(exp_at.timestamp())
        is_access_token = 1

        if is_refresh_token:
            exp_at = dt.timedelta(
                seconds=Consts.REFRESH_TOKEN_TTL) + server_time
            exp_at_ts = int(exp_at.timestamp())
            is_access_token = 0
        if user_id != Enums.UserRole.ADMIN.value:
            role = cls.encode_user_role(role)
        payload_jwt = {
            "iss": 'ora-sci',
            "exp": exp_at_ts,
            "iat": tzware_timestamp(),
            "app_id": "ora_sci",
            "_id": user_id,
            "role": role,
            "access_token": is_access_token
        }
        token = cls.generate_jwt_token(payload_jwt)
        return token

    @ classmethod
    def generate_jwt_token(cls, payload):
        encoded = jwt.encode(payload, Conf.SECRET_KEY, algorithm="HS256")
        return encoded

    @ classmethod
    def decode_jwt(self, token, options={}):
        try:
            payload = jwt.decode(token, Conf.SECRET_KEY, [
                                 "HS256"], options=options)
            return payload
        except:
            traceback.print_exc()
            return None

    @ classmethod
    def verify_signature(cls, signature, public_key, timestamp, address):
        # TODO: verify signature
        return address

    @classmethod
    def refresh_token(cls, refresh_token):
        """refresh token

        Args:
            refresh_token (str)

        Returns:
            (access_token, refresh_token) tuble
        """
        account_info = cls.decode_jwt(refresh_token)
        is_accessToken = py_.get(account_info, "access_token")
        uid = py_.get(account_info, str("_id"))
        if is_accessToken:
            return None, None
        user_obj = Repo.mUser.get_item_with({"_id": ObjectId(uid)})
        if not user_obj:
            return None, None
        user_role = py_.get(user_obj, "read_only.role")
        new_access_token = cls.generate_access_token(
            str(uid), user_role, is_refresh_token=False)
        new_refresh_token = cls.generate_access_token(
            str(uid), user_role, is_refresh_token=True)
        Repo.mUser.update_raw(
            {"_id": ObjectId(uid)},
            {
                "$set": {
                    "internal.last_access_token": new_access_token,
                    "last_login": tzware_timestamp()
                }
            }
        )
        return new_access_token, new_refresh_token

    @classmethod
    def auth_admin(cls, username, password):
        if username != Consts.ADMIN_USERNAME:
            return
        if password != Consts.ADMIN_PASSWORD:
            return
        access_token = cls.generate_access_token(
            Enums.UserRole.ADMIN.value, Enums.UserRole.ADMIN.value, is_refresh_token=False)
        refresh_token = cls.generate_access_token(
            Enums.UserRole.ADMIN.value, Enums.UserRole.ADMIN.value, is_refresh_token=True)
        server_time = tzware_datetime()
        response = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "server_time": int(server_time.timestamp())
        }
        return response

    @classmethod
    def sync_token(cls, user_id, access_token):
        # sync to redis
        _key = Consts.KEY_USER_TOKEN + user_id
        redis_cached.set(_key, access_token, 86400)
        if user_id == Enums.UserRole.ADMIN.value:
            return
        # sync to database
        Repo.mUser.update_raw({
            "_id": ObjectId(user_id)
        },
            {
            "$set": {
                "internal.last_access_token": access_token,
                "last_login": tzware_timestamp()
            }
        })
        return

    @classmethod
    def encode_user_role(cls, role_obj: dict):
        if not role_obj:
            return ""
        encoded = ""
        for role, status in role_obj.items():
            if status == 0:
                continue
            encoded += f"/{role}"
        encoded = encoded[1:] if len(encoded) > 0 else encoded
        return encoded

    @classmethod
    def decode_user_role(cls, role_encoded, output_type="dict"):
        list_role = role_encoded.split("/")
        if output_type == "list":
            return list_role

        if output_type == "dict":
            dict_resp = {}
            for default_role in Enums.UserRole.list():
                if default_role == Enums.UserRole.ADMIN.value():
                    continue
                dict_resp.update(
                    {
                        default_role: int(default_role in list_role)
                    })
            return dict_resp
