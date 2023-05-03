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
        'signature': fields.String(description='Signature', required=True),
        'public_key': fields.String(description='Public Key', required=True),
        'timestamp': fields.Integer(description="Timestamp", required=True),
        'address': fields.String(description='Address', required=True)
    })

    out_login = api.model('OutputLogin', {
        'access_token': fields.String(default=""),
        'refresh_token': fields.String(default=""),
        '_id': fields.String(default=""),
        'server_time': fields.Integer(),
    })

    resp_login = api.inherit("LoginResponse", response, {
        'data': fields.Nested(out_login, default={})
    })

    access_token = api.model('AccessToken', {
        'access_token': fields.String(default=""),
    })
