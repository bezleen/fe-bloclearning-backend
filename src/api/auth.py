from flask import request, current_app

from flask_restx import Resource, marshal
import pydash as py_

import src.constants as Consts
from src.schemas import AuthMeta
import src.decorators as Decorators
import src.controllers as Controllers
from src.extensions import redis_cached
from src.resp_code import ResponseMsg
import src.functions as funcs
from src.config import DefaultConfig as Conf
import src.enums as Enums
from src.utils.util_datetime import tzware_timestamp
from src.middlewares.http import enable_cors

api = AuthMeta.api


@api.route('/login')
@api.doc(responses=AuthMeta.RESPONSE_CODE)
class Login(Resource):
    """
        Login Resource
    """
    @api.expect(AuthMeta.in_login)
    @api.marshal_with(AuthMeta.resp_login)
    @enable_cors
    def post(self):
        data = marshal(request.get_json(), AuthMeta.in_login)
        signature = py_.get(data, "signature")
        public_key = py_.get(data, "public_key")
        timestamp = py_.get(data, 'timestamp')
        address = py_.get(data, 'address')
        resp = Controllers.Auth.authenticate_wallet_server_side(
            signature, public_key, timestamp, address)
        if not resp:
            return ResponseMsg.INVALID.to_json(data={}), 400
        return ResponseMsg.SUCCESS.to_json(data=resp), 200


@api.route('/admin-login')
@api.doc(responses=AuthMeta.RESPONSE_CODE)
class Login(Resource):
    """
        Login Admin Resource
    """
    @api.expect(AuthMeta.in_admin_login)
    @api.marshal_with(AuthMeta.resp_admin_login)
    @enable_cors
    def post(self):
        data = marshal(request.get_json(), AuthMeta.in_admin_login)
        username = py_.get(data, "username")
        password = py_.get(data, "password")
        resp = Controllers.Auth.auth_admin(username, password)
        if not resp:
            return ResponseMsg.INVALID.to_json(data={}), 400
        return ResponseMsg.SUCCESS.to_json(data=resp), 200


@api.route('/refresh-token')
@api.doc(responses=AuthMeta.RESPONSE_CODE)
class RefreshToken(Resource):
    """
        Refresh token
    """
    @api.expect(AuthMeta.in_refresh_token)
    @enable_cors
    def post(self):
        data = marshal(request.get_json(), AuthMeta.in_refresh_token)
        refresh_token = py_.get(data, "refresh_token")
        if not refresh_token:
            return ResponseMsg.INVALID.to_json(data={}), 400
        new_access_token, new_refresh_token = Controllers.Auth.refresh_token(
            refresh_token)

        return ResponseMsg.SUCCESS.to_json(data={
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        })


@api.route('/server-time')
@api.doc(responses=AuthMeta.RESPONSE_CODE)
class ServerTime(Resource):
    """
        Get current server time
    """
    @ api.marshal_with(AuthMeta.response)
    @enable_cors
    def get(self):

        return ResponseMsg.SUCCESS.to_json(data={
            "server_time": tzware_timestamp()
        })
