from flask_restx import Namespace, fields

from .api import BaseMeta


class Meta(BaseMeta):
    api = Namespace('User', description='')

    response = api.model('Response', {
        'msg': fields.String(default="unknown"),
        'code': fields.Integer(default=0),
        'data': fields.Raw()
    })

    out_profile = api.model('OutputProfile', {
        'user_id': fields.String(default=""),
        'name': fields.String(default=""),
        'avatar': fields.String(default=""),
        'last_login': fields.Integer(),
        'first_login': fields.Integer(),
    })

    resp_profile = api.inherit("ProfileResponse", response, {
        'data': fields.Nested(out_profile, default={})
    })

    in_update_profile = api.model('InputUpdateProfile', {
        'name': fields.String(description='New Name')
    })
