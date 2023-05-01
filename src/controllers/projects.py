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
    def get_all_projects(cls) -> list:
        _aggregate = [
            {"$match": {}},
            {
                "$project": {
                    "_id": 1,
                    "title": 1,
                    "main_tag": 1,
                    "overview": 1,
                    "thumbnail": 1,
                    "details": 1
                }
            },
            {"$sort": {"total": -1}},
            {"$limit": 10}
        ]
        all_projects = Repo.mProjects.aggregate(_aggregate)
        all_projects = list(all_projects)
        all_projects = list(map(lambda x: {
            "_id": str(x["_id"]),
            "title": x["title"],
            "main_tag": x["main_tag"],
            "overview": x["overview"],
            "thumbnail": x["thumbnail"],
            "details": x["details"]
        },
            all_projects))
        print(all_projects)
        return all_projects

    @classmethod
    def get_project_by_id(cls, project_id) -> list:
        project = Repo.mProjects.get_item_with({"_id": ObjectId(project_id)})
        team_members_id = py_.get(project, "team_members_id")
        team_members = []
        for team_member_id in team_members_id:
            member_info = cls.get_member_details(team_member_id)
            team_members.append(member_info)

        project_resp = {
            "_id": project_id,
            "author_id": py_.to_string(py_.get(project, "author_id")),
            "title": py_.get(project, "title"),
            "main_tag": py_.get(project, "main_tag"),
            "tag": py_.get(project, "tag"),
            "overview": py_.get(project, "overview"),
            "thumbnail": py_.get(project, "thumbnail"),
            "details": py_.get(project, "details"),
            "team_members": team_members,
            "content": py_.get(project, "content"),
            "at_a_glance": py_.get(project, "at_a_glance"),
            "updates": py_.get(project, "updates"),
            "date_created": int(py_.get(project, "date_created").timestamp())
        }
        return project_resp

    @classmethod
    def get_member_details(cls, member_id):
        member_details_1 = {
            "name": "Morten Scheibye-Knudsen",
            "role": "Research Lead",
            "description": ""
        }
        member_details_2 = {
            "name": "Matt Kaeberlein",
            "role": "",
            "description": "Professor at University of Washington and collaborator (to assess the long term healthspan and lifespan of mice after drug interventions)"
        }
        member_details_3 = {
            "name": "Simon Johnson",
            "role": "",
            "description": "Assistant Professor at University of Washington and collaborator (to evaluate the brain aging biology in the same animals with periodontal disease)"
        }
        member_detail = random.choice([member_details_1, member_details_2, member_details_3])
        return member_detail
