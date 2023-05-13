import datetime
from dateutil.relativedelta import relativedelta
from bson.objectid import ObjectId
import pytz
import os
import pydash as py_
from operator import itemgetter

import src.enums as Enums
from src.extensions import redis_cached
import src.controllers as Controllers
import src.constants as Consts
import src.models.repo as Repo
import json
import src.functions as funcs
from bson import json_util


class User(object):

    @classmethod
    def check_conflict_token(cls, user_id, access_token):
        _key = Consts.KEY_USER_TOKEN + user_id
        synced_token = redis_cached.get(_key) or ""
        return synced_token != access_token

    @classmethod
    def get_profile(cls, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        _filter = {"_id": user_id}
        user_info = Repo.mUser.get_item_with(_filter)
        current_role = py_.get(user_info, "read_only.role")
        if not user_info:
            return
        profile = {
            "user_id": str(user_id),
            "name": py_.get(user_info, "read_only.name"),
            "role": py_.filter_(list(current_role.keys()), lambda x: current_role[x] == 1),
            "avatar": py_.get(user_info, "read_only.avatar"),
            'occupation': py_.get(user_info, "read_only.occupation"),
            'work_at': py_.get(user_info, "read_only.work_at"),
            'location': py_.get(user_info, "read_only.location"),
            'contact': py_.get(user_info, "read_only.contact"),
            "last_login": py_.get(user_info, "internal.last_login"),
            "first_login": py_.to_integer(py_.get(user_info, "date_created").timestamp())
        }
        return profile

    @classmethod
    def update_profile(cls, user_id, name=None, occupation=None, work_at=None, location=None, contact=None):
        _update = {}
        if name:
            name = funcs.safe_name(name)
            _update.update(
                {"read_only.name": name, "name_idx": funcs.safe_string(name)})
        if occupation:
            _update.update({"read_only.occupation": occupation})
        if work_at:
            _update.update({"read_only.work_at": work_at})
        if location:
            _update.update({"read_only.location": location})
        if contact and funcs.is_valid_phone_number(contact):
            _update.update({"read_only.contact": contact})

        if not _update:
            return
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        _filter = {"_id": user_id}
        Repo.mUser.update_raw(_filter, {"$set": _update})
        return

    @classmethod
    def check_allowed_file(cls, file_name):
        return file_name.split(".")[-1] in ['png', 'jpg', 'jpeg', 'webp']

    @classmethod
    def delete_old_avatar(cls, file_name):
        file_path = os.path.join(Consts.UPLOAD_FOLDER, file_name)
        if os.path.exists(file_path):
            # delete the file
            os.remove(file_path)
        return

    @classmethod
    def upload_avatar(cls, user_id, file):
        if file.filename == '':
            raise ValueError("No file selected for uploading")
        if file and cls.check_allowed_file(file.filename):
            true_filename = f"{ObjectId()}.webp"
            path = os.path.join(Consts.UPLOAD_FOLDER, true_filename)
            file.save(path)
        else:
            raise ValueError("File is not allowed")
        # current avatar path
        user_info = Repo.mUser.get_item_with({"_id": ObjectId(user_id)})
        current_avatar = py_.get(
            user_info, "read_only.avatar").split("static/")[-1]
        if current_avatar not in Enums.Avatar.list():
            # delete current_avatar
            cls.delete_old_avatar(current_avatar)
        # save url_prefix
        Repo.mUser.update_raw(
            {
                "_id": ObjectId(user_id)
            },
            {
                "$set": {
                    "read_only.avatar": f"static/{true_filename}"
                }
            }
        )
        return
