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
    ATTACHED_FILE_ALLOW = ["zip"]

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
    def submit_form(cls, user_id, form_type, data):
        form_info = Repo.mForms.get_item_with(
            {
                "candidate_id": ObjectId(user_id),
                "status": {"$in": [Enums.FormStatus.UNPUBLISHED.value, Enums.FormStatus.PENDING.value]}
            })
        if form_info:
            return
        candidate_info = Controllers.User.get_profile(user_id)
        current_role = py_.get(candidate_info, "role")
        if py_.get(current_role, Consts.FORM_TO_ROLE[form_type], 0) == 1:
            return
        candidate_type = py_.get(data, "candidate_type")
        field = py_.get(data, "field"),
        email = py_.get(data, "email")
        candidate_name = py_.get(data, "name")
        occupation = py_.get(data, 'occupation')
        work_at = py_.get(data, 'work_at')
        location = py_.get(data, 'location')
        contact = py_.get(data, 'contact')
        # TODO: config the custom data
        custom_data = {}
        _id = ObjectId()
        obj = {
            "_id": _id,
            "type": form_type,
            "candidate_id": ObjectId(user_id),
            "card_id_front": None,
            "card_id_back": None,
            "attached_file_path": None,
            "candidate_name": candidate_name,
            "occupation": occupation,
            "work_at": work_at,
            "location": location,
            "contact": contact,
            "candidate_type": candidate_type,
            "email": email,
            "custom_data": custom_data,
            "status": Enums.FormStatus.UNPUBLISHED.value
        }
        if candidate_type == Enums.FormCandidateType.ORGANIZATION.value:
            obj["field"] = field
        Repo.mForms.insert(obj)
        return {"form_id": str(_id)}

    @classmethod
    def upload_card_id_img(cls, user_id, form_id, file, side):
        form_info = Repo.mForms.get_item_with({"_id": ObjectId(form_id)})

        if not form_info or py_.to_string(py_.get(form_info, "candidate_id")) != str(user_id):
            return

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
            return

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

    @classmethod
    def publish_form(cls, user_id, form_id):
        form_info = Repo.mForms.get_item_with({"_id": ObjectId(form_id)})
        if not form_info or py_.to_string(py_.get(form_info, "candidate_id")) != str(user_id):
            return False
        Repo.mForms.update_raw(
            {"_id": ObjectId(form_id)},
            {
                "$set": {
                    "status": Enums.FormStatus.PENDING.value
                }
            }
        )
        return

    @classmethod
    def fetch_forms(cls, page, page_size):
        forms = Repo.mForms.get_list({
            "status": Enums.FormStatus.PENDING.value
        }, page=page, page_size=page_size)
        forms = list(forms)
        resp_forms = []
        for form in forms:
            form_id = py_.get(form, "_id")
            form_type = py_.get(form, "type")
            form_status = py_.get(form, "status")
            candidate_id = py_.get(form, "candidate_id")
            candidate_name = py_.get(form, "candidate_name")
            candidate_info = Controllers.User.get_profile(candidate_id)
            current_role = py_.get(candidate_info, "role")
            avatar = py_.get(candidate_info, "avatar")
            resp_forms.append({
                "_id": str(form_id),
                "type": form_type,
                "candidate_id": str(candidate_id),
                "candidate_name": candidate_name,
                "current_role": py_.filter_(list(current_role.keys()), lambda x: current_role[x] == 1),
                "avatar": avatar,
                "status": form_status
            })
        return resp_forms

    @classmethod
    def get_form_by_id(cls, form_id):
        form_info = Repo.mForms.get_item_with({"_id": ObjectId(form_id)})
        if not form_info:
            return {}
        form_id = py_.get(form_info, "_id")
        form_type = py_.get(form_info, "type")
        form_status = py_.get(form_info, "status")
        candidate_id = py_.get(form_info, "candidate_id")
        card_id_front = py_.get(form_info, "card_id_front")
        card_id_back = py_.get(form_info, "card_id_back")
        attached_file_path = py_.get(form_info, "attached_file_path")
        custom_data = py_.get(form_info, "custom_data", {})
        # form data
        candidate_type = py_.get(form_info, "candidate_type")
        field = py_.get(form_info, "field"),
        email = py_.get(form_info, "email")
        candidate_name = py_.get(form_info, "candidate_name")
        occupation = py_.get(form_info, 'occupation')
        work_at = py_.get(form_info, 'work_at')
        location = py_.get(form_info, 'location')
        contact = py_.get(form_info, 'contact')
        # account data
        candidate_info = Controllers.User.get_profile(candidate_id)
        current_role = py_.get(candidate_info, "role")
        avatar = py_.get(candidate_info, "avatar")
        last_login = py_.get(candidate_info, "last_login")
        first_login = py_.get(candidate_info, "first_login")
        resp = {
            "_id": str(form_id),
            "type": form_type,
            "card_id_front": card_id_front,
            "card_id_back": card_id_back,
            "attached_file_path": attached_file_path,
            "custom_data": custom_data,
            "candidate_id": str(candidate_id),
            "candidate_name": candidate_name,
            "current_role": py_.filter_(list(current_role.keys()), lambda x: current_role[x] == 1),
            "avatar": avatar,
            "occupation": occupation,
            "work_at": work_at,
            "location": location,
            "contact": contact,
            "candidate_type": candidate_type,
            "email": email,
            "first_login": first_login,
            "last_login": last_login,
            "status": form_status
        }
        if candidate_type == Enums.FormCandidateType.ORGANIZATION.value:
            resp["field"] = field
        return resp

    @classmethod
    def approve_form(cls, form_id):
        form_info = Repo.mForms.get_item_with({"_id": ObjectId(form_id)})
        form_status = py_.get(form_info, "status")
        if not form_info or form_status != Enums.FormStatus.PENDING.value:
            return
        form_type = py_.get(form_info, "type")
        candidate_id = py_.get(form_info, "candidate_id")
        Repo.mUser.update_raw(
            {
                "_id": candidate_id
            },
            {
                "$set": {
                    f"read_only.role.{Consts.FORM_TO_ROLE[form_type]}": 1
                }
            })
        Repo.mForms.update_raw(
            {
                "_id": ObjectId(form_id)
            },
            {
                "$set": {
                    "status": Enums.FormStatus.DONE.value
                }
            })
        return

    @classmethod
    def reject_form(cls, form_id):
        form_info = Repo.mForms.get_item_with({"_id": ObjectId(form_id)})
        form_status = py_.get(form_info, "status")
        if not form_info or form_status != Enums.FormStatus.PENDING.value:
            return
        Repo.mForms.update_raw(
            {
                "_id": ObjectId(form_id)
            },
            {
                "$set": {
                    "status": Enums.FormStatus.REJECTED.value
                }
            })
        return

    @classmethod
    def fetch_my_forms(cls, user_id, page=1, page_size=10):
        forms = Repo.mForms.get_list({
            "candidate_id": ObjectId(user_id)
        }, page=page, page_size=page_size)
        forms = list(forms)
        resp_forms = []
        for form in forms:
            form_id = py_.get(form, "_id")
            form_type = py_.get(form, "type")
            form_status = py_.get(form, "status")
            candidate_id = py_.get(form, "candidate_id")
            candidate_name = py_.get(form, "candidate_name")
            candidate_info = Controllers.User.get_profile(candidate_id)
            current_role = py_.get(candidate_info, "role")
            avatar = py_.get(candidate_info, "avatar")
            resp_forms.append({
                "_id": str(form_id),
                "type": form_type,
                "candidate_id": str(candidate_id),
                "candidate_name": candidate_name,
                "current_role": py_.filter_(list(current_role.keys()), lambda x: current_role[x] == 1),
                "avatar": avatar,
                "status": form_status
            })
        return resp_forms

    @classmethod
    def get_my_form_by_id(cls, user_id, form_id):
        form_info = Repo.mForms.get_item_with({"_id": ObjectId(form_id)})
        if not form_info:
            return {}
        form_id = py_.get(form_info, "_id")
        form_type = py_.get(form_info, "type")
        form_status = py_.get(form_info, "status")
        candidate_id = py_.get(form_info, "candidate_id")
        if str(candidate_id) != str(user_id):
            return {}
        card_id_front = py_.get(form_info, "card_id_front")
        card_id_back = py_.get(form_info, "card_id_back")
        attached_file_path = py_.get(form_info, "attached_file_path")
        custom_data = py_.get(form_info, "custom_data", {})
        # form data
        candidate_type = py_.get(form_info, "candidate_type")
        field = py_.get(form_info, "field"),
        email = py_.get(form_info, "email")
        candidate_name = py_.get(form_info, "candidate_name")
        occupation = py_.get(form_info, 'occupation')
        work_at = py_.get(form_info, 'work_at')
        location = py_.get(form_info, 'location')
        contact = py_.get(form_info, 'contact')
        # account data
        candidate_info = Controllers.User.get_profile(candidate_id)
        current_role = py_.get(candidate_info, "role")
        avatar = py_.get(candidate_info, "avatar")
        last_login = py_.get(candidate_info, "last_login")
        first_login = py_.get(candidate_info, "first_login")

        resp = {
            "_id": str(form_id),
            "type": form_type,
            "card_id_front": card_id_front,
            "card_id_back": card_id_back,
            "attached_file_path": attached_file_path,
            "custom_data": custom_data,
            "candidate_id": str(candidate_id),
            "candidate_name": candidate_name,
            "current_role": py_.filter_(list(current_role.keys()), lambda x: current_role[x] == 1),
            "avatar": avatar,
            "occupation": occupation,
            "work_at": work_at,
            "location": location,
            "contact": contact,
            "candidate_type": candidate_type,
            "email": email,
            "first_login": first_login,
            "last_login": last_login,
            "status": form_status
        }
        if candidate_type == Enums.FormCandidateType.ORGANIZATION.value:
            resp["field"] = field
        return resp
