from flask_restx import Namespace, fields

from .api import BaseMeta


class Meta(BaseMeta):
    api = Namespace('Authentication', description='')

    response = api.model('Response', {
        'msg': fields.String(default="unknown"),
        'code': fields.Integer(default=0),
        'data': fields.Raw()
    })

    in_refresh_token = api.model('InputRefreshToken', {
        'refresh_token': fields.String(description='refresh_token')
    })

    in_login = api.model('InputLogin', {
        'custom_id': fields.String(description='Custom id')
    })

    out_login = api.model('OutputLogin', {
        'access_token': fields.String(default=""),
        'refresh_token': fields.String(default=""),
    })

    resp_login = api.inherit("LoginResponse", response, {
        'data': fields.Nested(out_login, default={})
    })

    access_token = api.model('AccessToken', {
        'access_token': fields.String(default=""),
    })
