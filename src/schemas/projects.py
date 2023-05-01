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
