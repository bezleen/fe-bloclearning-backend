import os
import random
import datetime
import json

from dateutil.relativedelta import relativedelta
from bson.objectid import ObjectId
import pydash as py_

import src.enums as Enums
from src.extensions import redis_cached
import src.controllers as Controllers
import src.constants as Consts
import src.models.repo as Repo
from src.utils.util_datetime import tzware_datetime, tzware_timestamp


class Projects(object):

    @classmethod
    def get_all_projects(cls, page=1, page_size=10) -> list:
        _filter = {}
        _aggregate = [
            {"$match": _filter},
            {
                "$project": {
                    "_id": 1,
                    "title": 1,
                    "main_tag": 1,
                    "tags": 1,
                    "overview": 1,
                    "thumbnail": 1,
                    "stage": 1,
                    "stage_detail": 1
                }
            },
            {"$sort": {"total": -1}},
            {"$skip": int((page - 1) * page_size)},
            {"$limit": page_size}
        ]
        all_projects = Repo.mProjects.aggregate(_aggregate)
        all_projects = list(all_projects)
        resp = []
        for project in all_projects:
            project_stage = py_.get(project, "stage")
            if project_stage == Enums.ProjectStage.PRE_QUALIFICATION.value:
                status = py_.get(
                    project, f"stage_detail.{project_stage}.approval", 0.0)
            elif project_stage == Enums.ProjectStage.REVIEWING.value:
                status = py_.get(
                    project, f"stage_detail.{project_stage}.approval", 0.0)
            elif project_stage == Enums.ProjectStage.FUNDING.value:
                status = py_.get(
                    project, f"stage_detail.{project_stage}.amount", 0.0)
            elif project_stage == Enums.ProjectStage.EXECUTING.value:
                status = py_.get(
                    project, f"stage_detail.{project_stage}.status", "unknown")
            elif project_stage == Enums.ProjectStage.COMPLETED.value:
                status = py_.get(
                    project, f"stage_detail.{project_stage}.status", "unknown")
            else:
                status = "unknown"
            project_summary = {
                "_id": py_.to_string(py_.get(project, "_id")),
                "title": py_.get(project, "title", ""),
                "main_tag": py_.get(project, "main_tag", ""),
                "tags": py_.get(project, "tags", []),
                "overview": py_.get(project, "overview", ""),
                "thumbnail": py_.get(project, "thumbnail"),
                "stage": py_.get(project, "stage"),
                "status": status
            }
            resp.append(project_summary)
        print(resp)
        return resp

    @classmethod
    def get_project_by_id(cls, project_id) -> list:
        project = Repo.mProjects.get_item_with({"_id": ObjectId(project_id)})
        if not project:
            return {}
        project_resp = {
            "_id": project_id,
            "author_id": py_.to_string(py_.get(project, "author_id")),
            "title": py_.get(project, "title"),
            "main_tag": py_.get(project, "main_tag"),
            "tags": py_.get(project, "tags"),
            "overview": py_.get(project, "overview"),
            "thumbnail": py_.get(project, "thumbnail"),
            "stage": py_.get(project, "stage"),
            "stage_detail": py_.get(project, "stage_detail"),
            "team_members": py_.get(project, "team_members"),
            "content": py_.get(project, "content"),
            "updates": py_.get(project, "updates"),
            "date_created": int(py_.get(project, "date_created").timestamp())
        }
        return project_resp

    @classmethod
    def init_project(cls, user_id, data):
        # extract data
        title = py_.get(data, "title")
        main_tag = py_.get(data, "main_tag")
        tags = py_.get(data, "tags", [])
        overview = py_.get(data, "overview")
        team_members = py_.get(data, "team_members")
        content = py_.get(data, "content")
        # initialize the project
        project_id = ObjectId()
        project_obj = {
            "_id": project_id,
            "author_id": ObjectId(user_id),
            "title": title,
            "main_tag": main_tag,
            "tags": tags,
            "overview": overview,
            "thumbnail": None,
            "stage": Enums.ProjectStage.UNPUBLISHED.value,
            "stage_detail": {},
            "team_members": team_members,
            "content": content,
            "updates": []
        }
        Repo.mProjects.insert(project_obj)
        return {"_id": str(project_id)}

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
    def upload_thumbnail(cls, user_id, project_id, file):
        project_info = Repo.mProjects.get_item_with(
            {"_id": ObjectId(project_id)})
        author_id = py_.get(project_info, "author_id")
        if str(author_id) != str(user_id):
            raise ValueError("Conflict Auth")
        if file.filename == '':
            raise ValueError("No file selected for uploading")
        if file and cls.check_allowed_file(file.filename):
            true_filename = f"{ObjectId()}.webp"
            path = os.path.join(Consts.UPLOAD_FOLDER, true_filename)
            file.save(path)
        else:
            raise ValueError("File is not allowed")
        # current thumbnail path
        thumbnail = py_.get(project_info, "thumbnail").split("static/")[-1]
        if thumbnail:
            # delete current_thumbnail
            current_thumbnail_path = thumbnail.split("static/")[-1]
            cls.delete_old_avatar(current_thumbnail_path)
        # save url_prefix
        Repo.mProjects.update_raw(
            {
                "_id": ObjectId(project_id)
            },
            {
                "$set": {
                    "thumbnail": f"static/{true_filename}"
                }
            }
        )
        return

    @classmethod
    def user_publish_project(cls, project_id, user_id):
        project_info = Repo.mProjects.get_item_with(
            {"_id": ObjectId(project_id)})
        if not project_info or py_.to_string(py_.get(project_info, "author_id")) != str(user_id):
            return False
        Repo.mProjects.update_raw(
            {"_id": ObjectId(project_id)},
            {
                "$set": {
                    "stage": Enums.ProjectStage.PENDING.value
                }
            }
        )
        return True

    @classmethod
    def admin_approve_project(self, project_id):
        project_info = Repo.mProjects.get_item_with(
            {"_id": ObjectId(project_id)})
        current_stage = py_.get(project_info, "stage")
        if current_stage != Enums.ProjectStage.PENDING.value:
            return False
        initiated_dt = tzware_datetime()
        Repo.mProjects.update_raw(
            {"_id": ObjectId(project_id)},
            {
                "$set": {
                    "stage": Enums.ProjectStage.PRE_QUALIFICATION.value,
                    "stage_detail.pre_qualified.initiated": int(initiated_dt.timestamp()),
                    "stage_detail.pre_qualified.approval": 0.0,
                    # FIXME: set dynamic
                    "stage_detail.pre_qualified.exp": int((initiated_dt + datetime.timedelta(seconds=60)).timestamp())
                }
            }
        )

    @classmethod
    def admin_reject_project(self, project_id):
        project_info = Repo.mProjects.get_item_with(
            {"_id": ObjectId(project_id)})
        current_stage = py_.get(project_info, "stage")
        if current_stage != Enums.ProjectStage.PENDING.value:
            return False
        Repo.mProjects.update_raw(
            {"_id": ObjectId(project_id)},
            {
                "$set": {
                    "stage": Enums.ProjectStage.REJECTED.value
                }
            }
        )
        return True
