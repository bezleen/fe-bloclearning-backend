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


class Form(object):
    CARD_ID_FILE_ALLOW = ['png', 'jpg', 'jpeg', 'webp']
    ATTACHED_FILE_ALLOW = ["pdf"]

    @classmethod
    def check_allowed_file(cls, file_name, allow_file=[]):
        return file_name.split(".")[-1] in allow_file

    @classmethod
    def delete_static_file(cls, file_name):
        file_path = os.path.join(Consts.UPLOAD_FOLDER, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
        return

    @classmethod
    def submit_form_researcher(cls, user_id, data):
        form_info = Repo.mForms.get_item_with({"candidate_id": ObjectId(user_id)})
        if form_info:
            return
        # TODO: parse the value from data
        custom_data = {}
        _id = ObjectId()
        obj = {
            "_id": _id,
            "type": Enums.FormType.OFFER_RESEARCHER.value,
            "candidate_id": ObjectId(user_id),
            "card_id_front": None,
            "card_id_back": None,
            "attached_file_path": None,
            "custom_data": custom_data,
            "publish": False
        }
        Repo.mForms.insert(obj)
        return {"form_id": _id}

    @classmethod
    def submit_form_third_party(cls, user_id, data):
        form_info = Repo.mForms.get_item_with({"candidate_id": ObjectId(user_id)})
        if form_info:
            return
        # TODO: parse the value from data
        custom_data = {}
        _id = ObjectId()
        obj = {
            "_id": _id,
            "type": Enums.FormType.OFFER_THIRD_PARTY.value,
            "candidate_id": ObjectId(user_id),
            "card_id_front": None,
            "card_id_back": None,
            "attached_file_path": None,
            "custom_data": custom_data,
            "publish": False
        }
        Repo.mForms.insert(obj)
        return {"form_id": _id}

    @classmethod
    def upload_card_id_img(cls, user_id, form_id, file, side):
        form_info = Repo.mForms.get_item_with({"_id": ObjectId(form_id)})

        if not form_info or py_.to_string(py_.get(form_info, "candidate_id")) != str(user_id):
            return False

        if file.filename == '':
            raise ValueError("No file selected for uploading")

        if file and cls.check_allowed_file(file.filename, allow_file=cls.CARD_ID_FILE_ALLOW):
            true_filename = f"{ObjectId()}.webp"
            path = os.path.join(Consts.UPLOAD_FOLDER, true_filename)
            file.save(path)
        else:
            raise ValueError("File is not allowed")

        # check current card_id path
        current_path = py_.get(form_info, f"card_id_{side}")
        if current_path:
            current_file_name = current_path.split("static/")[-1]
            cls.delete_static_file(current_file_name)

        # update card_id path
        Repo.mForms.update_raw(
            {"_id": ObjectId(form_id)},
            {
                "$set": {
                    f"card_id_{side}": f"static/{true_filename}"
                }
            }
        )
        return

    @classmethod
    def upload_attached_file(cls, user_id, form_id, file):
        form_info = Repo.mForms.get_item_with({"_id": ObjectId(form_id)})

        if not form_info or py_.to_string(py_.get(form_info, "candidate_id")) != str(user_id):
            return False

        if file.filename == '':
            raise ValueError("No file selected for uploading")

        if file and cls.check_allowed_file(file.filename, allow_file=cls.CARD_ID_FILE_ALLOW):
            true_filename = file.filename
            path = os.path.join(Consts.UPLOAD_FOLDER, true_filename)
            file.save(path)
        else:
            raise ValueError("File is not allowed")

        # check current card_id path
        attached_file_path = py_.get(form_info, "attached_file_path")
        if attached_file_path:
            current_file_name = attached_file_path.split("static/")[-1]
            cls.delete_static_file(current_file_name)

        # update card_id path
        Repo.mForms.update_raw(
            {"_id": ObjectId(form_id)},
            {
                "$set": {
                    "attached_file_path": f"static/{true_filename}"
                }
            }
        )
        return
