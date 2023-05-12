from flask_restx import Namespace, fields, marshal, reqparse

from src.schemas.api import BaseMeta


class Meta(BaseMeta):
    api = Namespace("Projects", description="")

    response = api.model("Response", {
        "msg": fields.String(default="unknown"),
        "code": fields.Integer(default=0),
        "data": fields.Raw()
    })

    # output_mails = api.model("response mails", {
    #     "mails": fields.List(fields.Raw(), default=[])
    # })
    team_members = api.model("Team member", {
        "name": fields.String(required=True),
        "role": fields.String(required=True),
        "description": fields.String(required=True)
    })

    in_initialize = api.model("Initialize a project", {
        "title": fields.String(required=True),
        "main_tag": fields.String(required=True),
        "tags": fields.List(fields.String()),
        "overview": fields.String(required=True),
        "team_members": fields.List(fields.Nested(team_members)),
        "content": fields.String(required=True)
    })
