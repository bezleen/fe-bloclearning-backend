import random
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
